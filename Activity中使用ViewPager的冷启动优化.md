---
title: Activity中使用ViewPager的冷启动优化
tags: Android 
---


## Activity中使用ViewPager的冷启动优化
> viewpager是android 中常用的控件，很多应用的主界面都是通过ViewPager+Fragment实现的，我们应用也是使用的这种实现方式。

#### 问题：
 ViewPager中包含5个Fragment，一进入时5个Fragment都构建出来，都会执行Fragment的`onCreateView`方法，导致一进入Activity时`onMeasure`执行过多，造成启动Activity时间过长
 
#### 解决方法：
1. 首先设置`ViewPager setOffscreenpageLimit`为1,这样默认一进入页面时只会缓存最多3个Fragment
2. 使用第一步的设置后，页面只会缓存左右各1个Fragment，当fragment被销毁时，在滑动回界面会重新执行，`onCreateView`,导致页面重新加载。为了解决该问题需要使用如下方法
```
private View rootView;
@Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        if (null != rootView) {
            ViewGroup parent = (ViewGroup) rootView.getParent();
            if (null != parent) {
                parent.removeView(rootView);
            }
        } else {
            rootView = inflater.inflate(layoutId, null);
            initView(rootView);// 控件初始化
        }
        return rootView;
    }
```
Fragment切换出去被销毁，再回到这个页面是Fragment对象还是同一个，但是回重新执行onCreateView方法，重新新建View。
为了不在生成新的view，我们在第一次执行onCreateView后将view保存到全局变量中，
下次再执行到onCreateView将上次保存的view返回出去，Fragment会把这个返回的view再添加到页面上，
效果来说仍然是之前的页面，对用户是无感知的。
3. 一般来说，Fragment的数据加载是写在`onCreateView`中的，我们在进入时只看到一个Fragment，对于不可见的Fragment我们可以先不做数据加载，当滑动到页面时再执行加载，减少不必要的操作。一般称之为 **懒加载 **
##### 关于懒加载
Fragment提供方法 `setUserVisibleHint(boolean isVisibleToUser)`
其中参数 `isVisibleToUser` 就表示Fragment对用户可见不可见
当tab滑动到对应的Fragment时，会调用该方法。
```
 /**
     * Set a hint to the system about whether this fragment's UI is currently visible
     * to the user. This hint defaults to true and is persistent across fragment instance
     * state save and restore.
     *
     * <p>An app may set this to false to indicate that the fragment's UI is
     * scrolled out of visibility or is otherwise not directly visible to the user.
     * This may be used by the system to prioritize operations such as fragment lifecycle updates
     * or loader ordering behavior.</p>
     *
     * <p><strong>Note:</strong> Prior to Android N there was a platform bug that could cause
     * <code>setUserVisibleHint</code> to bring a fragment up to the started state before its
     * <code>FragmentTransaction</code> had been committed. As some apps relied on this behavior,
     * it is preserved for apps that declare a <code>targetSdkVersion</code> of 23 or lower.</p>
     *
     * @param isVisibleToUser true if this fragment's UI is currently visible to the user (default),
     *                        false if it is not.
     */
    public void setUserVisibleHint(boolean isVisibleToUser) {
        // Prior to Android N we were simply checking if this fragment had a FragmentManager
        // set before we would trigger a deferred start. Unfortunately this also gets set before
        // a fragment transaction is committed, so if setUserVisibleHint was called before a
        // transaction commit, we would start the fragment way too early. FragmentPagerAdapter
        // triggers this situation.
        // Unfortunately some apps relied on this timing in overrides of setUserVisibleHint
        // on their own fragments, and expected, however erroneously, that after a call to
        // super.setUserVisibleHint their onStart methods had been run.
        // We preserve this behavior for apps targeting old platform versions below.
        boolean useBrokenAddedCheck = false;
        Context context = getContext();
        if (mFragmentManager != null && mFragmentManager.mHost != null) {
            context = mFragmentManager.mHost.getContext();
        }
        if (context != null) {
            useBrokenAddedCheck = context.getApplicationInfo().targetSdkVersion <= VERSION_CODES.M;
        }

        final boolean performDeferredStart;
        if (useBrokenAddedCheck) {
            performDeferredStart = !mUserVisibleHint && isVisibleToUser && mState < STARTED
                    && mFragmentManager != null;
        } else {
            performDeferredStart = !mUserVisibleHint && isVisibleToUser && mState < STARTED
                    && mFragmentManager != null && isAdded();
        }

        if (performDeferredStart) {
            mFragmentManager.performPendingDeferredStart(this);
        }

        mUserVisibleHint = isVisibleToUser;
        mDeferStart = mState < STARTED && !isVisibleToUser;
    }
```
注释已经说的很清楚，我们需要注意一下两点：
1. setUserVisibleHint 方法会执行多次
2. setUserVisibleHint可能会在onCreateView调用之前调用







