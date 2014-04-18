package wlan_positioning.test;

import android.app.Activity;
import android.content.Context;
import android.os.Vibrator;
import android.content.Context;
import android.content.SharedPreferences;
import android.media.RingtoneManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Environment;
import android.net.wifi.*;
import android.view.*;
import android.widget.*;
import java.io.OutputStream;
import java.io.InputStream;
import java.io.File;
import java.net.Socket;
import java.net.ServerSocket;
import android.net.Uri;
import java.util.List;
import java.util.Timer;
import android.database.sqlite.SQLiteDatabase;

public class Test extends Activity
{
    Wifi wifi;
    Handler handler;
    TextView v_show;
    Button v_start;
    EditText v_ip;
    EditText v_pt;
    static String path = Environment.getExternalStorageDirectory().getPath()+"/";
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
	
	//------------------------init--------------------
	wifi = new Wifi(this);
	handler = new Handler();
	v_show = (TextView)findViewById(R.id.show);
	v_start = (Button)findViewById(R.id.start);
	v_ip = (EditText)findViewById(R.id.ip);
	v_pt = (EditText)findViewById(R.id.pt);
	SharedPreferences pref = getSharedPreferences("pref",0);
	String ip = pref.getString("ip",null);
	if(ip!=null){
	    v_ip.setText(ip);
	}

	wifi.enable();
	v_start.setOnClickListener(new View.OnClickListener(){
		public void onClick(View v){
		    new Sender(getApplicationContext(), wifi, v_ip.getText().toString()).start();
		}
	    });
	new Receiver(handler, v_show, v_pt).start();
    }

    public void onDestroy(){
	super.onDestroy();
	SharedPreferences pref = getSharedPreferences("pref",0);
	SharedPreferences.Editor editor = pref.edit();
	editor.putString("ip",v_ip.getText().toString());
	editor.commit();
	System.exit(0);
    }

    public boolean onCreateOptionsMenu(Menu menu){
	menu.add("clear database");
	menu.add("clear screen");
	return true;
    }

    public boolean onOptionsItemSelected(MenuItem item){
	if(item.getTitle()=="clear database"){
	    SQLiteDatabase db = SQLiteDatabase.openOrCreateDatabase(path+"phone_test.db",null);
	    String sql = "delete from result";
	    db.execSQL(sql);
	    Toast.makeText(this,"database cleared",0).show();
	}
	if(item.getTitle()=="clear screen"){
	    Receiver.content = "";
	    v_show.setText("");
	}
	return false;
    }
}

class Wifi{
    private WifiManager mgr;
    public Wifi(Context context){
	mgr = (WifiManager)context.getSystemService(Context.WIFI_SERVICE);
    }
    public boolean is_enabled(){
	return mgr.isWifiEnabled();
    }
    public void enable(){
	mgr.setWifiEnabled(true);
    }
    public void disable(){
	mgr.setWifiEnabled(false);
    }
    public List<ScanResult> scan(){
	mgr.startScan();
	return mgr.getScanResults();
    }
}

class Sender extends Thread {
    String ip;
    Wifi wifi;
    Context context;
    String device;
    int delay = 3000;
    int interval = 1000;
    int times = 5;
    public Sender(Context context, Wifi wifi, String ip){
	this.ip = ip;
	this.wifi = wifi;
	this.context = context;
	device = android.os.Build.MODEL.trim().replace(' ','_');
	Task task = new Task(times);
	new Timer().schedule(task, delay, interval);
    }


    class Task extends java.util.TimerTask{
	int times;
	int cnt = 0;
	public Task(int times){
	    this.times = times;
	}
	public void run(){
	    cnt++;
	    //send
	    List<ScanResult> result_lst = wifi.scan();
	    String entry = "{";
	    for(int i=0;i<result_lst.size();++i){
		entry += "\""+result_lst.get(i).BSSID+"\""+":"+result_lst.get(i).level;
		if(i != result_lst.size()-1)
		    entry+=",";
		else
		    entry+="}";
	    }
	    entry = device+'\t'+entry;
	    try{
		Socket s = new Socket(ip,5672);
		OutputStream os = s.getOutputStream();
		os.write(entry.getBytes());
		os.close();
		s.close();
		System.out.println("----------------------------------send");
	    } catch(Exception e){
		e.printStackTrace();
	    }
	    //notify
	    if(cnt>=times){
		this.cancel();
		Vibrator vibrator = (Vibrator)context.getSystemService(Context.VIBRATOR_SERVICE);
		vibrator.vibrate(1000);
		Uri uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
		android.media.Ringtone rt = RingtoneManager.getRingtone(context, uri);
		if(rt != null)
		    rt.play();
	    }
	}
    }

}

class Receiver extends Thread{
    Handler handler;
    TextView v_show;
    ServerSocket ss;
    static String content;
    static String path = Environment.getExternalStorageDirectory().getPath()+"/";
    SQLiteDatabase db;
    EditText v_pt;
    String device;

    public Receiver(Handler handler, TextView v_show, EditText v_pt){
	this.handler = handler;
	this.v_show = v_show;
	this.v_pt = v_pt;
	content = "";
	device = android.os.Build.BRAND;

	db = SQLiteDatabase.openOrCreateDatabase(path+"phone_test.db",null);
	String sql = "create table if not exists result (reality, prediction)";
	db.execSQL(sql);

    }

    public void run(){
	super.run();
	listen();
    }

    public void listen(){
	try{
	    ss = new ServerSocket(5674);
	}catch(Exception e){
	    e.printStackTrace();
	}
	while(true){
	    try{
		Socket s = ss.accept();
		System.out.println("----------------------------------receive");
		InputStream is = s.getInputStream();
		byte[] buffer = new byte[1024];
		is.read(buffer);
		is.close();
		String prediction = new String(buffer).trim(); 
		content += " "+ prediction;
		//save into db
		String reality = "pt"+v_pt.getText().toString();
		System.out.println("----------------------------------real: "+reality+" predict: "+prediction);
		String sql = "insert into result values (?,?)";
		db.execSQL(sql, new String[]{reality,prediction});
		//change UI text 
		Runnable update_ui = new Runnable(){
			public void run(){
			    v_show.setText(content);
			}
		    };
		handler.post(update_ui);
	    } catch(Exception e){
		e.printStackTrace();
	    }
	}
    }

}