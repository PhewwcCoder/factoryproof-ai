import { getDocumentProxy } from 'unpdf';
import { parsePages } from './domain';
export async function extract(content: Uint8Array, filename: string) {
  if(content.byteLength>10*1024*1024)throw new Error('Maximum document size is 10 MB.');
  if(filename.toLowerCase().endsWith('.txt'))return parsePages([{page:1,text:new TextDecoder('utf-8',{fatal:true}).decode(content).slice(0,100000)}]);
  if(new TextDecoder().decode(content.slice(0,5))!=='%PDF-')throw new Error('The file is not a valid PDF.');
  const pdf=await getDocumentProxy(content,{useSystemFonts:false});
  try{
    if(pdf.numPages>100)throw new Error('Use a PDF with no more than 100 pages.');
    const pages=[];
    for(let i=1;i<=pdf.numPages;i++){const page=await pdf.getPage(i), text=await page.getTextContent();pages.push({page:i,text:text.items.map(item=>'str' in item?item.str.trim():'').filter(Boolean).join('\n').slice(0,40000)});}
    return parsePages(pages);
  } finally { await pdf.cleanup(); }
}

