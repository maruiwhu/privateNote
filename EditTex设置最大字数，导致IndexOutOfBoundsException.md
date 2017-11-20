
# EditTex设置最大字数，导致IndexOutOfBoundsException
Tags: Android


### 设置限制最大输入字数的方法
设置EditText输入框的最大字数可以有以下几种方式
1.在xml中设置` maxLength `
2.在代码中设置filter，如
`editText.setFilters(new InputFilter[]{new InputFilter.LengthFilter(20)});`
 即限定最大输入字符数为20
3.利用 TextWatcher 进行监听
### 异常场景
在英文环境下，在输入框中输入错误的英文字符，会出现纠错功能，
根据纠错功能，会弹出一个选择框，选择对应的文字，如果提示的文字超过字数限制，点击就会出现字符越界的异常
```java
 java.lang.IndexOutOfBoundsException: setSpan (0 ... 9) ends beyond length 4
 	at android.text.SpannableStringBuilder.checkRange(SpannableStringBuilder.java:1265)
 	at android.text.SpannableStringBuilder.setSpan(SpannableStringBuilder.java:684)
 	at android.text.SpannableStringBuilder.setSpan(SpannableStringBuilder.java:677)
 	at android.widget.Editor$SuggestionsPopupWindow.updateSuggestions(Editor.java:3650)
 	at android.widget.Editor$SuggestionsPopupWindow.show(Editor.java:3522)
 	at android.widget.Editor.replace(Editor.java:370)
 	at android.widget.Editor$3.run(Editor.java:2158)
 	at android.os.Handler.handleCallback(Handler.java:751)
 	at android.os.Handler.dispatchMessage(Handler.java:95)
 	at android.os.Looper.loop(Looper.java:176)
 	at android.app.ActivityThread.main(ActivityThread.java:6566)
 	at java.lang.reflect.Method.invoke(Native Method)
 	at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:899)
 	at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:789)
```
### 解决办法
	在xml文件中设置edtiText的 android:inputType=”textNoSuggestions”