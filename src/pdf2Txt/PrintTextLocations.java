import org.apache.pdfbox.cos.COSDocument;
import org.apache.pdfbox.pdfparser.PDFParser;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.util.PDFTextStripper;
import org.apache.pdfbox.util.TextPosition;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Vector;

public class PrintTextLocations extends PDFTextStripper{
	private String parsedText;
	private Vector<List<TextPosition>> textPos;
	public PrintTextLocations() throws IOException{
			parsedText = "";
			textPos = new Vector<List<TextPosition>>();
	        super.setSortByPosition( true );
	}
	public Vector<List<TextPosition>> getCharactersByArticle()
	{ 
		return charactersByArticle; 
	}
	public String getParsedText(){
		return parsedText;
	}
	public Vector<List<TextPosition>> getTextPos(){
		return textPos;
	}
	public int pdftoText(String fileName, int startPage, int endPage) {
		PDFParser parser = null;
		PrintTextLocations pdfStripper = null;
		PDDocument pdDoc = null;
		COSDocument cosDoc = null;
		int pcount=0;
		File file = new File(fileName);
		if (!file.isFile()) {
			System.err.println("File " + fileName + " does not exist.");
			//return null;
		}
		try {
			parser = new PDFParser(new FileInputStream(file));
		} catch (IOException e) {
			System.err.println("Unable to open PDF Parser. " + e.getMessage());
			//return null;
		}
		try {
			parser.parse();
			cosDoc = parser.getDocument();
			pdfStripper = new PrintTextLocations();
			pdDoc = new PDDocument(cosDoc);
			pcount=pdDoc.getNumberOfPages();
			pdfStripper.setStartPage(startPage);
			pdfStripper.setEndPage(endPage);
			parsedText = pdfStripper.getText(pdDoc);
			textPos = pdfStripper.getCharactersByArticle();
		} catch (Exception e) {
			System.err
					.println("An exception occured in parsing the PDF Document."
							+ e.getMessage());
		} finally {
			try {
				if (cosDoc != null)
					cosDoc.close();
				if (pdDoc != null)
					pdDoc.close();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
		return pcount;
		
	}
	
	public String formatContents(){
		ArrayList<String> page = new ArrayList<String>();
		String formattedContents ="";
		ArrayList<Integer> indents = new ArrayList<Integer>();
		String line="";
		int y = -1;
		int x = -1;
		int x_pre = -1;
		//int lineCounter = 0;
		int x_start = -1;
		for (int i=0;i<textPos.size();++i){
			for(int j=0;j<textPos.get(i).size();++j){
				if(y != (int)textPos.get(i).get(j).getY()){
					y = (int)textPos.get(i).get(j).getY();
					if (!line.equals("")){
						if (x - x_pre > 4 && x_pre != -1){
							page.add("\n");
							indents.add(-1000);
						}
						line = line+"\n";
						page.add(line);
						indents.add(x_start);
						line="";
						x_pre=x;
					}
					x_start = (int) textPos.get(i).get(j).getX();
				}
				line=line+textPos.get(i).get(j).getCharacter();
				x = (int)textPos.get(i).get(j).getX();
				}
		}
		if (x - x_pre > 4 && x_pre != -1){
			page.add("\n");
			indents.add(-1000);
		}
		page.add(line);
		indents.add(x_start);
		
		
		Set<Integer>  indentSet=new HashSet<Integer>();
		for (Integer i: indents)
			indentSet.add(i);
		Map<Integer, Integer> indentNum = new HashMap<Integer, Integer>();
		int dis = 10000;
		ArrayList<Integer> ic = new ArrayList<Integer>();
		ic.addAll(indentSet);
		Collections.sort(ic);
		int num =0;
		//for (int i=0;i<ic.size();++i)
		//System.out.println(ic.get(i));
		if (ic.size()> 1){
			for (int i=1;i<ic.size();++i ){
				dis = (int)ic.get(i) - (int)ic.get(i-1);
				if (dis < 30 && dis > 8){
					indentNum.put((int)ic.get(i-1), num);
					num+=1;
					indentNum.put((int)ic.get(i), num);
				}	
			}
		}
		
		else if(ic.size()>0){
			indentNum.put(ic.get(0), num);
		}
		for (int i=0;i<page.size();++i){
			if(page.get(i).indexOf("•") != -1)
				continue;
			String idts = "";
			if (!indentNum.containsKey(indents.get(i)))
				indentNum.put(indents.get(i), 0);
			for (int j=0; j<indentNum.get(indents.get(i)).intValue();j++){
				
				idts +="\t";
			}
			formattedContents += idts+page.get(i);
			
		}
		//System.out.println(formattedContents);
		return formattedContents;
	}
	
	
	
}

