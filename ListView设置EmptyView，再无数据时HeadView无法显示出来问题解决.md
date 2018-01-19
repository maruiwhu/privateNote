---
title: ListView设置EmptyView，再无数据时HeadView无法显示出来问题解决
tags: ListView,EmptyView,HeaderView
grammar_cjkRuby: true
grammar_code: true
---
## ListView设置EmptyView，再无数据时HeadView无法显示出来问题解决
### 背景
通常我们如果有个页面显示列表，同时会对列表为空的时候再设置一个空白页面，这个时候我们通常使用ListView->AdapterView 提供的setEmptyView方法，设置一个EmptyView，有系统控件判断，如果列表为空时自动显示空界面。
但是如果我们的ListView存在一个HeaderView，此时ListView的主体内容为空时，会直接显示EmptyView，HeaderView无法显示，那么如果我们想显示HeaderView该如何处理呢？
### 原理

为了解决我们的问题，首先我们需要了解ListView 控制EmptyView显示合隐藏的机制时怎么样的

1. 首先看setEmptyView的试下，在AdapterView中
    ```Java
    /**
     * Sets the view to show if the adapter is empty
     */
    @android.view.RemotableViewMethod
    public void setEmptyView(View emptyView) {
        mEmptyView = emptyView;

        // If not explicitly specified this view is important for accessibility.
        if (emptyView != null
                && emptyView.getImportantForAccessibility() == IMPORTANT_FOR_ACCESSIBILITY_AUTO) {
            emptyView.setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_YES);
        }

        final T adapter = getAdapter();
        final boolean empty = ((adapter == null) || adapter.isEmpty());
        updateEmptyStatus(empty);
    }
	```
	可以看到这里有个变量empty ，当adapter为null，或者adapter 的isEmpty方法为true时 empty为true，
	将这个变量值传给了方法updateEmptyStatus
	继续跟 updateEmptyStatus
	```java
	/**
     * Update the status of the list based on the empty parameter.  If empty is true and
     * we have an empty view, display it.  In all the other cases, make sure that the listview
     * is VISIBLE and that the empty view is GONE (if it's not null).
     */
    private void updateEmptyStatus(boolean empty) {
        if (isInFilterMode()) {
            empty = false;
        }

        if (empty) {
            if (mEmptyView != null) {
                mEmptyView.setVisibility(View.VISIBLE);
                setVisibility(View.GONE);
            } else {
                // If the caller just removed our empty view, make sure the list view is visible
                setVisibility(View.VISIBLE);
            }

            // We are now GONE, so pending layouts will not be dispatched.
            // Force one here to make sure that the state of the list matches
            // the state of the adapter.
            if (mDataChanged) {           
                this.onLayout(false, mLeft, mTop, mRight, mBottom); 
            }
        } else {
            if (mEmptyView != null) mEmptyView.setVisibility(View.GONE);
            setVisibility(View.VISIBLE);
        }
    }
	```
	其中isInFilterMode 是false
	```java
	/**
     * Indicates whether this view is in filter mode. Filter mode can for instance
     * be enabled by a user when typing on the keyboard.
     *
     * @return True if the view is in filter mode, false otherwise.
     */
    boolean isInFilterMode() {
        return false;
    }
	```
	updateEmptyStatus的逻辑就是根据empty的值来控制EmptyView和ListView的显示和隐藏
	也即是adapter为null或者adapter的isEmpty方法返回true时会显示EmptyView。
	### 解决方法
	根据上面的原理可知，如果我们重写Adapter的isEmpty方法，控制sEmpty的返回值，就可以控制EmptyView的显示和隐藏了。
	```java
	public boolean isEmpty() {
        return getCount() == 0;
    }
	```
	BaseAdapter的isEmpty是根据getCount的返回值来判断的
	如果我们重写isEmpty，恒返回false的话，只有ListView未设置adapter时会显示EmptyView，其他情况都会显示ListView。
	针对我们的问题，如果ListView存在HeaderView，我们可以使isEmpty返回false，如果不存在HeaderView，可以使isEmpty返回super的值，这样就可以在ListView主体为空时，仍然能显示HeaderView了
	
	
