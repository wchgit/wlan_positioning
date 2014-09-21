package wlan_positioning.client;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Environment;
import android.net.wifi.*;
import android.view.*;
import android.widget.*;
import java.io.OutputStream;
import java.io.InputStream;
import java.net.*;
import java.util.*;
import java.util.logging.*;
import android.hardware.SensorManager;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.util.Log;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.BroadcastReceiver;

public class Client extends Activity
{
    private Handler handler;
    private TextView v_show;
    private TextView v_acc;
    private TextView v_orien;
    private Button v_start;
    private EditText v_ip;
    private ScrollView v_scroll;
    public static WifiManager mgr;
    //--sensor
    private static SensorManager snsr_mgr;
    private static Sensor accelerometer;
    private static Sensor orientation;
    private static AccListener accListener;
    private static OrienListener orienListener;
    private ArrayList<String> step_seq;
    private AvailableReceiver availableReceiver;
    //--
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
	
	//------------------------init--------------------
	mgr = (WifiManager)getSystemService(Context.WIFI_SERVICE);
	handler = new Handler();
	v_show = (TextView)findViewById(R.id.show);
	v_acc = (TextView)findViewById(R.id.acc);
	v_orien = (TextView)findViewById(R.id.orien);
	v_start = (Button)findViewById(R.id.start);
	v_ip = (EditText)findViewById(R.id.ip);
	v_scroll = (ScrollView)findViewById(R.id.sv);
	SharedPreferences pref = getSharedPreferences("pref",0);
	String ip = pref.getString("ip",null);
	if(ip!=null){
	    v_ip.setText(ip);
	}

	step_seq = new ArrayList<String>();
	Wifi.enable(mgr);
	PosListener posListener = new PosListener(v_ip.getText().toString(), step_seq, handler, v_start);
	v_start.setOnClickListener(posListener);
	//--sensor
	accListener = new AccListener(step_seq, handler, v_acc);
	orienListener = new OrienListener(handler, v_orien);
	snsr_mgr = (SensorManager)getSystemService(SENSOR_SERVICE);
	accelerometer = snsr_mgr.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
	orientation = snsr_mgr.getDefaultSensor(Sensor.TYPE_ORIENTATION);
	register();
	//--
	IntentFilter fltr = new IntentFilter();
	fltr.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);
	availableReceiver = new AvailableReceiver();
	registerReceiver(availableReceiver,fltr);
	Wifi.scan(mgr);

	new Receiver(handler, v_show, v_scroll).start();
    }

    public static void register(){
	int delay = 200000;
	snsr_mgr.registerListener(accListener,accelerometer,delay);
	snsr_mgr.registerListener(orienListener,orientation,delay);
	//snsr_mgr.registerListener(accListener,accelerometer,SensorManager.SENSOR_DELAY_NORMAL);
	//snsr_mgr.registerListener(orienListener,orientation,SensorManager.SENSOR_DELAY_NORMAL);
	//snsr_mgr.registerListener(accListener,accelerometer,SensorManager.SENSOR_DELAY_FASTEST);
	//snsr_mgr.registerListener(orienListener,orientation,SensorManager.SENSOR_DELAY_FASTEST);
    }

    public static void unregister(){
	snsr_mgr.unregisterListener(accListener, accelerometer);
	snsr_mgr.unregisterListener(orienListener, orientation);
    }

    protected void onResume(){
	super.onResume();
	register();
    }

    protected void onPause(){
	super.onPause();
	unregister();
    }

    public void onDestroy(){
	super.onDestroy();
	SharedPreferences pref = getSharedPreferences("pref",0);
	SharedPreferences.Editor editor = pref.edit();
	editor.putString("ip",v_ip.getText().toString());
	editor.commit();
	unregister();
	unregisterReceiver(availableReceiver);
	System.exit(0);
    }
}

class AvailableReceiver extends BroadcastReceiver{
    public void onReceive(Context c, Intent i){
	Wifi.scan(Client.mgr);
    }
}

class PosListener implements View.OnClickListener{
    private boolean isStarted;
    private String ip;
    private Timer timer;
    private Handler handler;
    private Button v_start;
    private ArrayList<String> step_seq;
    private Task task;
    public PosListener(String ip, ArrayList<String> step_seq, Handler handler, Button v_start){
	isStarted = false;
	this.ip = ip;
	this.handler = handler;
	this.v_start = v_start;
	this.step_seq = step_seq;
    }
    public void onClick(View v){
	if(isStarted == false){
	    isStarted = true;
	    handler.post(new UpdateButton(v_start,"stop"));
	    timer = new Timer(true);
	    task = new Task(ip, step_seq);
	    timer.schedule(task,1000,1000);
	}else{
	    isStarted = false;
	    handler.post(new UpdateButton(v_start,"start"));
	    timer.cancel();
	}
    }
}
class Task extends TimerTask{
    private int cnt;
    private String ip;
    private String device;
    private ArrayList<String> step_seq;
    private String TAG = "wch";
    private String uid;
    private Logger logger;
    private static String path = Environment.getExternalStorageDirectory().getPath()+"/";

    public Task(String ip, ArrayList<String> step_seq){
	this.ip = ip;
	this.step_seq = step_seq;
	cnt = 0;
	device = android.os.Build.MODEL.trim().replace(' ','_');
	uid = "1234567";
	//logging info for testing, remove in the future
	logger = Logger.getLogger("test info");
	FileHandler handler;
	java.util.logging.Formatter formatter = new java.util.logging.Formatter(){
		public String format(LogRecord record){
		    return record.getMessage()+"\n";
		}
	    };
	try{
	    handler = new FileHandler(path+"test.log",true);
	    handler.setFormatter(formatter);
	    logger.addHandler(handler);
	}catch(Exception e){
	    e.printStackTrace();
	}

    }

    public void run(){
	List<ScanResult> result_lst = Wifi.getResult();
	String entry = "{";
	for(int i=0;i<result_lst.size();++i){
	    entry += "\""+result_lst.get(i).BSSID+"\""+":"+result_lst.get(i).level;
	    if(i != result_lst.size()-1)
		entry+=",";
	}
	entry+="}";
	
	String seq = "[";
	for(int i=0;i<step_seq.size();++i){
	    seq += "\""+step_seq.get(i)+"\"";
	    if(i != step_seq.size()-1)
		seq+=",";
	}
	seq+="]";
	step_seq.clear();

	long timestamp = new Date().getTime();
	
	entry = uid+'\t'+seq+'\t'+entry+'\t'+timestamp;
	//logging info for testing, remove in the future
	logger.info(entry);

	new Sender(ip,entry).start();
    }
}

//--------------------->>>>>>>>>>>>>>>>>>>>>UDP SENDER
class Sender extends Thread{
    String ip;
    String content;
    String TAG = "wch";
    public Sender(String ip, String content){
	this.ip = ip;
	this.content = content;
    }

    public void run(){
	try{
	    Log.d(TAG,"new run");
	    DatagramSocket dataSocket = new DatagramSocket();
	    byte[] sendDataByte = content.getBytes();
	    DatagramPacket dataPacket = new DatagramPacket(sendDataByte, sendDataByte.length,InetAddress.getByName(ip), 5672);
	    dataSocket.send(dataPacket);
	    Log.d(TAG,"run end");
	} catch(Exception e){
	    Log.d(TAG,"sender exception");
	    e.printStackTrace();
	}
    }
}

//--------------------->>>>>>>>>>>>>>>>>>>>>TCP SENDER
/*
class Sender extends Thread{
    String ip;
    String content;
    String TAG = "wch";
    public Sender(String ip, String content){
	this.ip = ip;
	this.content = content;
    }

    public void run(){
	try{
	    Socket s = new Socket(ip,5672);
	    OutputStream os = s.getOutputStream();
	    os.write(content.getBytes());
	    os.close();
	    s.close();
	} catch(Exception e){
	    e.printStackTrace();
	}
    }
}
*/

//--------------------->>>>>>>>>>>>>>>>>>>>>TCP RECEIVER
/*
class Receiver extends Thread{
    Handler handler;
    TextView v_show;
    ScrollView v_scroll;
    ServerSocket ss;
    String content;
    private String TAG = "wch"; //
    public Receiver(Handler handler, TextView v_show, ScrollView v_scroll){
	this.handler = handler;
	this.v_show = v_show;
	this.v_scroll = v_scroll;
	content = "";
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
		InputStream is = s.getInputStream();
		byte[] buffer = new byte[1024];
		is.read(buffer);
		is.close();
		content += " "+new String(buffer).trim();
		System.out.println("++++++++++++++++++++++++++++++++"+content);
		Runnable update_ui = new Runnable(){
			public void run(){
			    v_show.setText(content+"\n");
			    v_scroll.fullScroll(ScrollView.FOCUS_DOWN);
			}
		    };
		handler.post(update_ui);
	    } catch(Exception e){
		e.printStackTrace();
	    }
	}
    }
}
*/
//--------------------->>>>>>>>>>>>>>>>>>>>>UDP RECEIVER
class Receiver extends Thread{
    Handler handler;
    TextView v_show;
    ScrollView v_scroll;
    DatagramSocket dataSocket;
    String content;
    private String TAG = "wch"; //
    public Receiver(Handler handler, TextView v_show, ScrollView v_scroll){
	this.handler = handler;
	this.v_show = v_show;
	this.v_scroll = v_scroll;
	content = "";
    }

    public void run(){
	super.run();
	listen();
    }

    public void listen(){
	try {
	    dataSocket = new DatagramSocket(5674);
	    byte[] receiveByte = new byte[4096];
	    DatagramPacket dataPacket = new DatagramPacket(receiveByte, receiveByte.length);
	    while (true){
		dataSocket.receive(dataPacket);
		content += " "+new String(receiveByte, 0, dataPacket.getLength());
		System.out.println("++++++++++++++++++++++++++++++++"+content);
		Runnable update_ui = new Runnable(){
			public void run(){
			    v_show.setText(content+"\n");
			    v_scroll.fullScroll(ScrollView.FOCUS_DOWN);
			}
		    };
		handler.post(update_ui);
	    }
	} catch (Exception e) {
	    e.printStackTrace();
	}
    }
}

//--sensor
class AccListener implements SensorEventListener{
    private String TAG = "wch"; //
    private ArrayList<Float> acc_vals;
    private ArrayList<String> step_seq;
    private float lowThresh;
    private float highThresh;
    private int cnt;
    private Handler handler;//
    private TextView vAction;//
    private Step step;
    private boolean isWalking;
    private final int window_size = 20;

    public AccListener(ArrayList<String> step_seq, Handler handler, TextView vAction){
	this.handler = handler;//
	this.vAction = vAction;//
	this.step_seq = step_seq;
	acc_vals = new ArrayList<Float>(window_size);
	lowThresh = 10f;
	highThresh = 100f;
	cnt = 0;
	isWalking = false;
	step = new Step();
    }
    public void onSensorChanged(SensorEvent event){
	float [] values = event.values;
	float val = values[1]*values[1]+values[2]*values[2];
	if(acc_vals.size()<window_size)
	    acc_vals.add(val);
	else{
	    acc_vals.remove(0);
	    acc_vals.add(val);
	}

	float mean = Statistic.mean(acc_vals);
	float var = Statistic.var(acc_vals,mean);
	if((isWalking==true && var<lowThresh) || (isWalking==false && var<highThresh)){
	    //stop
	    cnt = 0;
	    handler.post(new UpdateTextView(vAction,"stop "+var));
	}
	else{
	    //walking
	    if(step.isNewStep(val)){
		cnt++;
		step_seq.add(OrienListener.orien);
	    }
	    handler.post(new UpdateTextView(vAction,"walk "+cnt+" "+var));
	}
    }

    class Step{
	private float trough;
	private float crest;
	private float lastlast;
	private float last;
	private float thresh;
	private boolean isCrest;
	public Step(){
	    trough = -100f; crest = 100f;
	    lastlast = -100f; last = -100f;
	    thresh = 15f;
	    isCrest = false;
	}
	public boolean isNewStep(float val){
	    isCrest = false;
	    if(last>lastlast && last>val && Math.abs(last-trough)>thresh){
		crest = last;
		isCrest = true;
	    }
	    else if(last<lastlast && last<val && Math.abs(last-crest)>thresh){
		trough = last;
	    }
	    lastlast = last;
	    last = val;
	    return isCrest;
	}
    }
    public void onAccuracyChanged(Sensor sensor, int accuracy){}
}

class OrienListener implements SensorEventListener{
    public static String orien;
    public static String orien_name;
    private TextView vDirection;
    private Handler handler;
    private String TAG = "wch";
    public OrienListener(Handler handler, TextView vDirection){
	this.vDirection = vDirection;
	this.handler = handler;
    }
    public void onSensorChanged(SensorEvent event){
	float [] values = event.values;
	float azimuth = values[0];
	orien = String.valueOf(azimuth);
	if(azimuth>=315 || azimuth<45)
	    orien_name = "N";
	else if(azimuth>=45 && azimuth<135)
	    orien_name = "E";
	else if(azimuth>=135 && azimuth<225)
	    orien_name = "S";
	else
	    orien_name = "W";
	handler.post(new UpdateTextView(vDirection,orien_name));
    }
    public void onAccuracyChanged(Sensor sensor, int accuracy){}
}

class UpdateTextView implements Runnable{
    TextView view; String content;
    public UpdateTextView(TextView view, String content){
	this.content = content;	this.view = view;
    }
    public void run(){ view.setText(content); }
};

class UpdateButton implements Runnable{
    Button view; String content;
    public UpdateButton(Button view, String content){
	this.content = content;	this.view = view;
    }
    public void run(){ view.setText(content); }
};

class Statistic{
    public static float mean(ArrayList<Float> a){
	float sum = 0;
	for(Float i : a)
	    sum += i;
	return sum/a.size();
    }
    public static float var(ArrayList<Float> a, float mean){
	float sum = 0;
	for(Float i : a)
	    sum += (i-mean)*(i-mean);
	return sum/a.size();
    }
}
//--

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
