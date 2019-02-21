import java.io.IOException;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.lang3.StringUtils;

public class Book {
    private String toc;
    private int toc_start;
    private int content_start;
    private ArrayList<ArrayList<String>> titles ;
    private int pcount;
    private String fileName;
    private int index_start;
    private int index_end;
    private String tocpath;
    private int content_end;
    private int isTOC;
    public Book(String fileName, int toc_start,  int content_start, int content_end, int index_start, int index_end, int isTOC){
    	toc="";
    	this.fileName=fileName;
    	titles=new ArrayList<ArrayList<String>>();
    	this.content_start=content_start;
    	this.toc_start=toc_start;
    	this.content_end = content_end;
    	this.index_start = index_start;
    	this.index_end = index_end;
    	this.isTOC = isTOC;
    }
    public void setTOC(String toc){
    	this.toc=toc;
    }
	//extract toc 
	public String getToc() throws IOException{
		int toc_end=content_start;
		if(content_start<=toc_start)
			toc_end=toc_start+15;
		int flag=2;
		String l0="1";
		String l1="";
		String l2="";
		String l0_pre="";
		String l1_pre="";
		PrintTextLocations ptl = new PrintTextLocations();
		pcount = ptl.pdftoText(fileName,toc_start,toc_end);
		String parsedText= ptl.getParsedText();
		if (isTOC==0){
			//System.out.println(parsedText);
			return parsedText;
		}
		
		System.out.println(parsedText);
		Matcher m;
		int i=0;
		String[] lines = parsedText.split("\\n|\\r|\\n\\r");
		while ( i < lines.length){
			if(l2 != "" && Pattern.matches("^\\s*(Chapter|CHAPTER|C H A P T E R)*\\s*"+l2+"(.+?)$", lines[i]) == true){
				//System.out.println(lines[i].charAt(lines[i].length()-1));
				//System.out.println(Character.isDigit(lines[i].charAt(lines[i].length()-1)));
				if (l1 == ""){
					throw new IOException("the format of the table of cotent is wrong");
				}
				m=Pattern.compile("^\\s*(Chapter|CHAPTER|C H A P T E R)*\\s*("+l2+"(.+?))$").matcher(lines[i]);
				while (m.find()){
					toc+=m.group(2).replace("fi ","fi").replaceAll("fl ","fl");
				}
				if(lines[i].matches("^.+?\\d\\s*$")){
				//if(Character.isDigit(lines[i].charAt(lines[i].length()-1))){
					//System.out.println("222222");
					//System.out.println(lines[i]);
					flag =1;
					toc+="\n";
				}
				else{
					flag =0;
				}
				
				l2=l1_pre+"."+(Integer.parseInt(l2.split("[\\.-]")[l2.split("[\\.-]").length-1])+1);
			}
			else if(l1 != "" && Pattern.matches("^\\s*(Chapter|CHAPTER|C H A P T E R)*\\s*"+l1+"(.+?)$", lines[i]) == true){
				
				if (l0 == ""){
					throw new IOException("the format of the table of cotent is wrong");
				}
				m=Pattern.compile("^\\s*(Chapter|CHAPTER|C H A P T E R)*\\s*("+l1+".+)$").matcher(lines[i]);
				while (m.find()){
					toc+=m.group(2).replace("fi ","fi").replaceAll("fl ","fl");
				}
				if(lines[i].matches("^.+?\\d\\s*$")){
				//if(Character.isDigit(lines[i].charAt(lines[i].length()-1))){
					//System.out.println("1111111");
					//System.out.println(lines[i]);
					flag =1;
					toc+="\n";
				}
				else{
					flag = 0;
				}
				l2=l1+".1";
				l1_pre=l1;
				if (l0.endsWith("\\."))
					l1=l0_pre+(Integer.parseInt(l1.split("[\\.-]")[l1.split("[\\.-]").length-1])+1);
				else
					l1=l0_pre+"."+(Integer.parseInt(l1.split("[\\.-]")[l1.split("[\\.-]").length-1])+1);
				
			}
			
			else if(Pattern.matches("^\\s*(Chapter|CHAPTER|C H A P T E R)*\\s*"+l0+"(.+?)$", lines[i]) == true){
				
				m=Pattern.compile("^\\s*(Chapter|CHAPTER|C H A P T E R)*\\s*("+l0+".+)$").matcher(lines[i]);
				while (m.find()){
					System.out.println(m.group(2));
					toc+=m.group(2).replace("fi ","fi").replaceAll("fl ","fl");
					
				}
				
				if (l0.endsWith("\\."))
					l1 = l0 +"1";
				else
					l1=l0+".1";
				if(lines[i].matches("^.+?\\d\\s*$")){
				//if(Character.isDigit(lines[i].charAt(lines[i].length()-1))){
					//System.out.println("00000000");
					//System.out.println(lines[i]);
					flag =1;
					toc+="\n";
				}
				else{
					flag = 0;
				}
				l0_pre=l0;
				l0=Integer.parseInt(l0)+1+"";
			}
			
			else{
				if(flag == 0){
					toc+=" "+lines[i];
					if(lines[i].matches("^.+?\\d$")){
						
						flag = 1;
						toc+="\n";
					}	
				}
			}
			i=i+1;
			
		}
		System.out.println(toc);
		return toc;
	}
	
	// parse toc to get section number,section title and page
	@SuppressWarnings("unchecked")
	public  ArrayList<ArrayList<String>> parseTOC() {
		Pattern page_pattern = Pattern.compile("\\d+\\s*$");
		Pattern dots=Pattern.compile("(\\.\\s*){3}");
		ArrayList<String> sec=new ArrayList<String>();
		Matcher dmat;
		String sep="";
		Matcher pmat;
		String page;
		for(String line:toc.split("\\n")){
			page="";
			sep="";
			//System.out.println(line);
			dmat=dots.matcher(line);
			while(dmat.find()){
				sep=dmat.group().trim();
			}
			if(sep == ""){
				sep=" ";
			}
			
			pmat = page_pattern.matcher(line);
			while(pmat.find()){
				page += pmat.group(0);
				
			}
			//System.out.println(page);
			if(sep.equals(" ")){
				sec.add(line.substring(0,line.lastIndexOf(sep)));
			}
			else{
				sec.add(line.substring(0,line.indexOf(sep)));
			}
			sec.add(page+"");
			
			titles.add((ArrayList<String>) sec.clone());
			sec.clear();
		}
		//System.out.println(titles);
		return titles;
	}
	
	
	
	public String getIndex (int start, int end) throws IOException{
		PrintTextLocations ptl = new PrintTextLocations();
		String parsedText ="";
		for (int i=start+content_start-1;i<=end+content_start-1;++i){
			ptl.pdftoText(fileName,i,i);
			ptl.getParsedText();
			parsedText += ptl.formatContents();
		}
		return parsedText;
	}
	public String getContent(int start, int end,  String currentSecTitle, String nextSecTitle ) throws IOException{
		String nextTitle="";
		String[] nts = nextSecTitle.split(" ");
		for(int i=1;i<nts.length;++i)
			nextTitle+=" "+nts[i];
		String currentTitle="";
		String[] cts = currentSecTitle.split(" ");
		for(int i=1;i<cts.length;++i)
			currentTitle+=" "+cts[i];
		end=end>0?end:content_end;
		String content="";
		int lineNum=0; //number of lines appears in this section; for some special cases that have a table of contents at the begginning of a book chapter; see chapter 1 of internet master book
		int flag=0;//where the section starts
		String currentSec=currentSecTitle.split(" ")[0];
		String nextSec=nextSecTitle.split(" ")[0];
		//deal with the first page and the last page of a section
		//String parsedText=pdftoText(fileName,start+content_start-1,start+content_start-1);
		PrintTextLocations ptl = new PrintTextLocations();
		String parsedText ="";
		for (int i=start+content_start-1;i<=start+content_start;++i){
			ptl.pdftoText(fileName,i,i);
			parsedText += ptl.getParsedText().replaceAll("fl ","fl").replace("fi ","fi");
		}
		//System.out.println(parsedText);
		for (String line:parsedText.split("\\n|\\r|\\r\\n")){
			
			//chapters are in seperated pages
			if (currentSec.indexOf(".") == -1 && currentSec.indexOf("-") == -1) {
				flag=1;
			}
			else{
				if(line.trim().startsWith(currentSec) && line.indexOf("|") == -1 
						&& line.indexOf("•") == -1){
					if( fuzzyContains(currentSecTitle.trim().toLowerCase(),
							line.trim().toLowerCase(), currentSec) ){
							flag=1;
					}
				}
			}
			if((line.trim().startsWith(nextSec) && line.indexOf("|") == -1 
					&& line.indexOf("•") == -1) || isExercise(line, currentSec)){
				if(fuzzyContains(nextSecTitle.trim().toLowerCase(),line.trim().toLowerCase(), nextSec)
						){	
					if (lineNum>3)
						break;	
				}
			}
			if(flag==1){
				content+=line+"\n";
				lineNum+=1;
			}
		}
		if (start+content_start-1==end+content_start-1)
			return content;
		for (int i=start+content_start;i<=end+content_start-2;++i){
			ptl.pdftoText(fileName,i,i);
			for(String line:ptl.getParsedText().replaceAll("fl ","fl").replace("fi ","fi").split("\\r\\n|\\n|\\r"))
					content=content+line+"\n";
		}
		parsedText="";
		for (int i=end+content_start-2;i<=end+content_start-1;++i){
			ptl.pdftoText(fileName,i,i);
			parsedText += ptl.getParsedText().replaceAll("fl ","fl").replace("fi ","fi");
		}
		flag=1;
		for (String line:parsedText.split("\\n|\\r|\\r\\n")){
			//chapters are in seperated pages
			if((line.trim().startsWith(nextSec) && line.indexOf("|") == -1 
					&& line.indexOf("•") == -1) || isExercise(line, currentSec)){
				if(fuzzyContains(nextSecTitle.trim().toLowerCase(),line.trim().toLowerCase(), nextSec)){
					if (lineNum>3)
						break;	
				}
			}
				content+=line+"\n";
				lineNum+=1;
		}
		return content;
		//return formatParagraph(content);
	}
	public static boolean isExercise(String line, String sec){
		line = line.toLowerCase();
		String sec_new ="";
		for (int i=0; i<sec.length();++i){
			sec_new+=sec.charAt(i)+" ";
		}
		sec_new = sec_new.trim();
		System.out.println("SEC_NEW_NEW");
		System.out.println(sec_new);
		
		if ( line.indexOf("exercise") > 0 || line.indexOf("e x e r c i s e") > 0 ){
			if (line.indexOf(sec) > 0 || line.indexOf(sec_new)>0 )
				return true;
		}
			
		return false;
	}
	public static boolean fuzzyContains(String s1, String s2, String sec){
		boolean contains = false;
		int l1 = s1.split(" ").length;
		int l2 = s2.split(" ").length;
		float dis=0;
		
		int i=0;
		for (i=0; i<Math.min(l1,l2); ++i){
			dis = StringUtils.getLevenshteinDistance(s1.split(" ")[i], s2.split(" ")[i])/(float)Math.max(l1, l2);
			//System.out.println(s1.split(" ")[i]);
			//System.out.println(s2.split(" ")[i]);
			//System.out.println(dis);
			if (dis > 0.4 )
				break;
		}
		if (i == Math.min(l1,l2))
			contains = true;
		int counter=0;
		if (!contains){
			//System.out.println(s1);
			//System.out.println(s2);
			for(String s: s2.split(" ")){
				if (s1.indexOf(s) != -1){
					//System.out.println("HIT "+s);
					counter += 1;
				}
			}
		}
		if ((float)counter/(float)s2.split(" ").length > 0.6)
			contains = true;
		return contains;
	}
	/*public static boolean fuzzyContains(String s1, String s2, String sec){
		boolean contains = false;
		int l1 = s1.split(" ").length;
		int l2 = s2.split(" ").length;
		float sim=0;
		if (s2.indexOf(sec) == -1 || s2.split(" ")[0].indexOf(s1.split(" ")[0]) == -1)
			return contains;
		int i=1;
		for (i=1; i<Math.min(l1,l2); ++i){
			
			sim = StringUtils.getLevenshteinDistance(s1.split(" ")[i], s2.split(" ")[i])/Math.max(l1, l2);
			if (sim > 0.8 )
				break;
		}
		if (i == Math.min(l1,l2))
			contains = true;
		return contains;
	}*/
	public static String formatParagraph(String contents){
		String paragraph ="";
		int flag=0;
		
		for (char c: contents.toCharArray()){
			if (c == '\n' && flag != 2){
				if (flag == 0)
					flag = 1;
				else if (flag == 1 )
					flag =2;
				paragraph+=" ";
			}
			else if (c == '\n' && flag==2){
				paragraph += "\n";
				flag=0;
			}
			else if (c == '\t'){
				flag = 0;
				paragraph += "\n"+"\t";
			}
			else{
				flag = 0;
				paragraph += c;
			}
		}
		
		return paragraph;
	}
	
}
/*if (currentSec.indexOf(".") == -1) 
				flag=1;
			if(line.indexOf(currentSec)!=-1){
					ct="";
				if (line.indexOf(" ")== -1)
					ct="wohahahahhahaha";
				else
					ct = line.substring(line.indexOf(" "));
				
				if( line.indexOf(currentTitle)!=-1 || currentTitle.indexOf(ct)!=-1 fuzzyContains(currentTitle,line) ){
					if (!line.matches("^.+?"+String.valueOf(end)+"$") && !line.matches("^.+?"+String.valueOf(start)+"$")  )
						flag=1;
					
				}
			}
			if(line.indexOf(nextSec)!=-1){
				nt="";
				if (line.indexOf(" ")== -1)
					nt="wohahahahhahaha";
				else
					nt = line.substring(line.indexOf(" "));
				if( line.indexOf(nextTitle)!=-1 || nextTitle.indexOf(nt)!=-1 ){
					if (!line.matches("^.+?"+String.valueOf(end)+"$") && !line.matches("^.+?"+String.valueOf(start)+"$")  )
						break;
					
				}
			}
			if(flag==1){
			}
 * */
 
