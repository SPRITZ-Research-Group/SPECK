package com.example.vulnerableapp;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.net.Uri;

public class Rule2ContentProvider extends ContentProvider {
    static final String AUTHORITY = "speck.rule2";
    static final Uri CONTENT_URI = Uri.parse("content://speck.rule2/rule2");
    static final String CREATE_TBL_QRY = " CREATE TABLE rule2 (_id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL);";
    static final String C_DATA = "data";
    static final String C_ID = "_id";
    static final String DBNAME = "rule2.db";
    static final int DBVERSION = 1;
    static final String DROP_TBL_QRY = "DROP TABLE IF EXISTS rule2";
    static final String TABLE = "rule2";
    SQLiteDatabase mDB;

    private static class DBHelper extends SQLiteOpenHelper {
        public DBHelper(Context context) {
            super(context, Rule2ContentProvider.DBNAME, (SQLiteDatabase.CursorFactory) null, 1);
        }

        public void onCreate(SQLiteDatabase db) {
            db.execSQL(Rule2ContentProvider.DROP_TBL_QRY);
            db.execSQL(Rule2ContentProvider.CREATE_TBL_QRY);
            db.execSQL("INSERT INTO rule2(data) VALUES ('some data');");
            db.execSQL("INSERT INTO rule2(data) VALUES ('some other data');");
        }

        public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
            onCreate(db);
        }
    }

    public int delete(Uri uri, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException("Not yet implemented");
    }

    public String getType(Uri uri) {
        return "vnd.android.cursor.item/vnd.speck.rule2";
    }

    public Uri insert(Uri uri, ContentValues values) {
        throw new UnsupportedOperationException("Not yet implemented");
    }

    public boolean onCreate() {
        SQLiteDatabase writableDatabase = new DBHelper(getContext()).getWritableDatabase();
        this.mDB = writableDatabase;
        if (writableDatabase == null) {
            return false;
        }
        return true;
    }

    public Cursor query(Uri uri, String[] projection, String selection, String[] selectionArgs, String sortOrder) {
        if(uri.equals(CONTENT_URI)) {
            String id = selection;
            String queryStr = C_ID+"="+ id;
            return mDB.query(TABLE, null, queryStr, null, null, null, null);
        }
        throw new IllegalArgumentException("unknown uri " + uri);
    }

    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException("Not yet implemented");
    }
}
