package wlan_positioning.collector;

import android.app.Activity;
import android.os.Bundle;
import android.os.Environment;
import android.os.Vibrator;
import android.content.Context;
import android.media.RingtoneManager;
import java.util.*;
import java.io.File;
import java.io.FileOutputStream;
import android.widget.*;
import android.net.wifi.*;
import android.net.Uri;
import android.view.View;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.BroadcastReceiver;
import android.util.Log;

public class Collector extends Activity implements View.OnClickListener, NumberPicker.OnValueChangeListener, CompoundButton.OnCheckedChangeListener
{
    //--------widget-----------
    private CheckBox state;
    private ImageView btn;
    private ProgressBar bar;
    private NumberPicker np;
    private TextView pt_slct;
    //--------param------------
    private int delay = 3000;
    private int interval = 1000;
    private int times = 500;
    private int cnt = 0;
    //--------viriable---------
    private String TAG = "wch";
    public static WifiManager mgr;
    private static String path = Environment.getExternalStorageDirectory().getPath()+"/";
    private static HashMap map;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
	//----------------------------------variable-----------------------------
	pt_slct = (TextView)findViewById(R.id.pt_selected);
	btn = (ImageView)findViewById(R.id.collect);
	bar = (ProgressBar)findViewById(R.id.progress);
	state = (CheckBox)findViewById(R.id.wifi_enabled);
	mgr = (WifiManager)getSystemService(Context.WIFI_SERVICE);
	//------------------------------------init-------------------------------
	map = new HashMap();
	bar.setMax(times);
	btn.setOnClickListener(this);
	np = (NumberPicker)findViewById(R.id.x_coord);
	np.setMaxValue(50);
	np.setMinValue(0);
	np.setOnValueChangedListener(this);
	if(Wifi.is_enabled(mgr))
	    state.setChecked(true);
	else
	    state.setChecked(false);
	state.setOnCheckedChangeListener(this);
    }

    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked){
	if(isChecked)
	    Wifi.enable(mgr);
	else
	    Wifi.disable(mgr);
    }

    public void onValueChange(NumberPicker picker, int oldVal, int newVal){
	pt_slct.setText("selected: pt"+newVal);
    }

    public void onClick(View v){
	map.clear();
	IntentFilter fltr = new IntentFilter();
	fltr.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);
	registerReceiver(new AvailableReceiver(),fltr);
	Wifi.scan(mgr);
    }

    class AvailableReceiver extends BroadcastReceiver{
	private int cnt;
	private String pid;
	public AvailableReceiver(){
	    cnt = 0;
	    bar.setProgress(cnt);
	    pid = "pt"+np.getValue();
	}
	public void onReceive(Context c, Intent intent){
	    Wifi.scan(mgr);
	    cnt++;
	    bar.setProgress(cnt);
	    List<ScanResult> result_lst = Wifi.getResult();
	    String line = new String();
	    for(int i=0;i<result_lst.size();++i){
		ScanResult result = result_lst.get(i);
		line += result.BSSID+"@"+String.valueOf(result.level)+" ";
		map.put(result.BSSID, result.SSID);
	    }
	    line = pid+"\t"+line+"\n";
	    //Log.d(TAG,line);
	    try{
		File file = new File(path+pid);
		FileOutputStream fos = new FileOutputStream(file,true);
		fos.write(line.getBytes());
		fos.close();		    
	    }catch(Exception e){
		e.printStackTrace();
	    }
	    if(cnt>=times){
		//----------------write ssid-bssid map to file--------------------
		try{
		    File file2 = new File(path+"SSID.txt");
		    FileOutputStream fos2 = new FileOutputStream(file2,true);
		    Set set = map.entrySet();
		    Iterator iter = set.iterator();
		    fos2.write((pid+"\t").getBytes());
		    while(iter.hasNext()){
			fos2.write((iter.next().toString()+"\t").getBytes());
		    }
		    fos2.write("\n".getBytes());
		    fos2.close();		    
		}catch(Exception e){
		    e.printStackTrace();
		}		    
		//----------------notify vibrate--------------------
		Vibrator vibrator = (Vibrator)getSystemService(Context.VIBRATOR_SERVICE);
		vibrator.vibrate(1000);
		//----------------notify ring-----------------------
		Uri uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
		android.media.Ringtone rt = RingtoneManager.getRingtone(getApplicationContext(), uri);
		if(rt != null)
		    rt.play();
		//Log.d(TAG,"done");
		unregisterReceiver(this);
	    }
	}
    }
}

class Wifi{
    public static List<ScanResult> result;
    public static boolean is_enabled(WifiManager mgr){
	return mgr.isWifiEnabled();
    }
    public static void enable(WifiManager mgr){
	mgr.setWifiEnabled(true);
    }
    public static void disable(WifiManager mgr){
	mgr.setWifiEnabled(false);
    }
    public static void scan(WifiManager mgr){
	mgr.startScan();
	result = mgr.getScanResults();
    }
    public static List<ScanResult> getResult(){
	return result;
    }
}

/*
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
    public String[] get_ssid(List<ScanResult> result){
	String [] ssids = new String[result.size()];
	for(int i=0;i<result.size();++i){
	    ssids[i] = result.get(i).SSID;
	}
	return ssids;
    }
    public String[] get_bssid(List<ScanResult> result){
	String [] bssids = new String[result.size()];
	for(int i=0;i<result.size();++i){
	    bssids[i] = result.get(i).BSSID;
	}
	return bssids;
    }
    public int[] get_level(List<ScanResult> result){
	int [] levels = new int[result.size()];
	for(int i=0;i<result.size();++i){
	    if(result.get(i)!=null)
		levels[i]=result.get(i).level;
	    else
		levels[i] = -100;
	}
	return levels;
    }
}
*/