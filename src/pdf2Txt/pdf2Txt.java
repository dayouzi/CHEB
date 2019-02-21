import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.FileOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import org.apache.commons.io.FileUtils;
/*precalculus 11 33 912 999 1010
network_masters 6 11 458 588 595 */
public class pdf2Txt {
	public static void parseNoToc(String bookName,int toc_start,int content_start, int content_end,int index_start, int index_end, int isTOC) throws Exception{
		
		String basepath="/home/sxw327/Dropbox/BookCreation/book/test/"+bookName+"/";
		//String basepath="D:/Dropbox/BookCreation/book/test/"+bookName+"/";
		String fileName=basepath+bookName+".pdf";
		String path=basepath+bookName+"_content/";
		String tocPath=basepath+bookName+".toc";
		
		new File(path).mkdir();
		System.out.println(path);
		File dir = new File(path);
		if (dir.exists())
			FileUtils.deleteDirectory(dir);
		new File(path).mkdir();
		//BufferedWriter wtoc = new BufferedWriter(new FileWriter(new File(tocPath)));
		//BufferedWriter wtoc = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(tocPath),"UTF-8"));
		Book ptp= new Book(fileName,toc_start,content_start,content_end,index_start,index_end, isTOC);
		String toc="";
		
		ArrayList<ArrayList<String>> titles = new ArrayList<ArrayList<String>>();
		if(isTOC == 0){
			PrintWriter wtoc = new PrintWriter(new OutputStreamWriter(new FileOutputStream(tocPath),"UTF-8"));
			toc=ptp.getToc();
			System.out.println(toc);
			String[] tocs=toc.split("\\n|\\r|\\r\\n");
			for(int i=0;i<tocs.length;++i){
				if(tocs[i].length()==0)
					continue;
				wtoc.write(tocs[i].replaceAll("’", "'").replaceAll("–","-").replaceAll("—", "-")+"\n");
				}
			wtoc.close();
			return ;
			}
		else if (isTOC==1){
			PrintWriter wtoc = new PrintWriter(new OutputStreamWriter(new FileOutputStream(tocPath),"UTF-8"));
			toc=ptp.getToc();
			String[] tocs=toc.split("\\n|\\r|\\r\\n");
			for(int i=0;i<tocs.length;++i){
				if(tocs[i].length()==0)
					continue;
				wtoc.write(tocs[i].replaceAll("’", "'").replaceAll("–","-").replaceAll("—", "-")+"\n");
				}
			wtoc.close();
			titles = ptp.parseTOC();
			System.out.println(titles);
			genContents(tocs,titles, ptp, path);
			
			
		}
		else{
			toc = readFile(tocPath,"UTF-8");	
			String[] tocs=toc.split("\\n|\\r|\\r\\n");
			ptp.setTOC(toc);
			titles = ptp.parseTOC();
			System.out.println(titles);
			genContents(tocs,titles, ptp, path);
		}
		
	}
	public static String readFile(String path, String encoding) throws IOException {
			  byte[] encoded = Files.readAllBytes(Paths.get(path));
			  return new String(encoded, encoding);
	}
	
	public static void write(String path, String content) {
	      String s = new String();
	      String s1 = new String();
	      try {
	       File f = new File(path);
	       if (!f.exists()) {
	    	   f.createNewFile();
	       }
	       BufferedReader input = new BufferedReader(new FileReader(f));
	       while ((s = input.readLine()) != null) {
	        s1 += s + "\n";
	       }
	       input.close();
	       s1 += content;
	       BufferedWriter output = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(f),"UTF-8"));
	       output.write(s1);
	       output.close();
	      } catch (Exception e) {
	       e.printStackTrace();
	      }
	}
	public static void genContents(String[] tocs,ArrayList<ArrayList<String>> titles, Book ptp,String path) throws IOException{
		String secTitle="";
		String nextTitle="";
		int start=0;
		int end=0;
		for(int i=0;i<tocs.length;++i){
			start=Integer.parseInt(titles.get(i).get(1).trim());
			//secID=titles.get(i).get(0);
			secTitle=titles.get(i).get(0);
			if(i==tocs.length-1){
				end=-1;
				nextTitle="wolegedacanimeiayaobunengting";
			}
			else{
				end=Integer.parseInt(titles.get(i+1).get(1).trim());
				nextTitle=titles.get(i+1).get(0);
			}
			 String content = ptp.getContent(start,end,secTitle,nextTitle);
			 System.out.println("generating "+i+" "+path+tocs[i].replaceAll("[\\=\\:\\!\\?\\%\\s]","_"));
			 //write(path+i+"",new String(content.getBytes("UTF-8"), "UTF-8")); 
			 write(path+i+"",content.replaceAll("’", "'").replaceAll("–","-").replaceAll("—", "-").replaceAll("“","\"").replace("”","\""));
		}
		// String index = ptp.getIndex(index_start, index_end);
		 //System.out.println("generating index");
		// write(path+"Index",new String(index.getBytes("UTF-8"), "UTF-8")); 
	}
	public static void main(String[] args) throws Exception{
		//Map <String, List> para = new HashMap();
		int toc_start=11;
		int content_start=33;
		int content_end = 912;
		int index_start = 999;
		int index_end = 1010;
		int isTOC=1; // 0: not toc exists and no parse 1: toc not exists and auto  parse 2: toc exists and parse
		String bookName="precalculus";
		
		//int toc_start=11;
		//int content_start=41;
		//int content_end = 891;
		//int index_start=611;
		//int index_end=625;
		//String bookName="macroeconomics";
		
		//parseIndex(bookName, index_start,index_end,toc_start,content_start);
		
		parseNoToc( bookName,toc_start,content_start,content_end, index_start, index_end,isTOC);
		
	}
	
}

