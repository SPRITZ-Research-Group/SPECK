package com.speck.android.tools;

import android.content.Context;
import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Adapter;

import com.speck.android.MainActivity;
import com.speck.android.R;

public class CustomAnimator {
    private Animation animation = null;
    private Context context;

    public CustomAnimator(Context context){
        this.context = context;
    }

    public void startAnimation(View view, int time, int xml){
        animation = AnimationUtils.loadAnimation(context, xml);
        animation.setDuration(time);
        view.startAnimation(animation);
        resetAnimation();
    }

    private void resetAnimation(){
        this.animation = null;
    }
}
