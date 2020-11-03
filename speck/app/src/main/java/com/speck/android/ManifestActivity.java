package com.speck.android;

import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import android.text.SpannableString;
import android.text.SpannableStringBuilder;
import android.text.style.ForegroundColorSpan;
import android.widget.TextView;
import androidx.appcompat.widget.Toolbar;

import com.speck.android.tools.FileReader;

public class ManifestActivity extends AppCompatActivity{

    private String manifest = "";
    private Context ctx;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.manifest_layout);
        ctx = this;

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setDisplayShowHomeEnabled(true);


        Intent intent = getIntent();
        manifest = intent.getStringExtra(ReportActivity.MANIFEST_DATA);

        new LoadManifest().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);

    }

    private class LoadManifest extends AsyncTask<Void, Void, Void> {

        private ProgressDialog progress = null;
        private SpannableStringBuilder builder = null;

        @Override
        protected Void doInBackground(Void... params) {
            FileReader fr = new FileReader(ctx, manifest);

            builder = new SpannableStringBuilder();
            String manifest_str = "\n" + fr.read().replace(">",">   \n").replace("<","   <");
            String[] splitted = manifest_str.split(" ");
            int size = splitted.length;

            for (int i = 0; i < size; i++){
                SpannableString str = new SpannableString(splitted[i] + " ");
                if (splitted[i].contains("<")){
                    str.setSpan(new ForegroundColorSpan(Color.parseColor("#cc0000")), 0, str.length(), 0);
                    builder.append(str);
                } else if (splitted[i].contains("=")){
                    String[] arg = splitted[i].split("=");
                    if (arg.length > 1) {
                        String end = "";
                        String value;
                        String space = " ";
                        if (arg[1].contains(">")) {
                            space = "";
                            if (arg[1].contains("?>")) {
                                value = arg[1].replace("?>", "");
                                end = "?>";
                            } else if (arg[1].contains("/>")){
                                value = arg[1].replace("/>", "");
                                end = "/>";
                            } else {
                                value = arg[1].replace(">", "");
                                end = ">";
                            }
                        } else{
                            value = arg[1];
                        }
                        SpannableString str1 = new SpannableString(arg[0]);
                        SpannableString str2 = new SpannableString(value + space);
                        SpannableString sep = new SpannableString("=");
                        SpannableString ending = new SpannableString(end);

                        str1.setSpan(new ForegroundColorSpan(Color.parseColor("#5A6351")), 0, str1.length(), 0);
                        str2.setSpan(new ForegroundColorSpan(Color.parseColor("#0000cc")), 0, str2.length(), 0);
                        ending.setSpan(new ForegroundColorSpan(Color.parseColor("#cc0000")), 0, ending.length(), 0);
                        sep.setSpan(new ForegroundColorSpan(Color.parseColor("#000000")), 0, sep.length(), 0);

                        builder.append(str1);
                        builder.append(sep);
                        builder.append(str2);
                        builder.append(ending);
                    }
                } else{
                    builder.append(str);
                }
            }

            return null;
        }

        @Override
        protected void onPostExecute(Void result) {
            TextView text = findViewById(R.id.data_manifest);
            text.setText(builder, TextView.BufferType.SPANNABLE);

            progress.dismiss();
            super.onPostExecute(result);
        }

        @Override
        protected void onPreExecute() {
            progress = ProgressDialog.show(ctx, null, "Loading AndroidManifest.xml...");
            super.onPreExecute();
        }
    }

}
