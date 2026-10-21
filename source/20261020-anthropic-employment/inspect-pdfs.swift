import PDFKit
import AppKit
let base=CommandLine.arguments[1]
var records:[[String:Any]]=[]
for (name,pageIndex) in [("employment",3),("expectations",7)] {
 let doc=PDFDocument(url:URL(fileURLWithPath:base+"/"+name+".pdf"))!
 let text=(0..<doc.pageCount).map{doc.page(at:$0)!.string ?? ""}.joined(separator:"\n")
 try text.write(toFile:base+"/"+name+"-extracted.txt",atomically:true,encoding:.utf8)
 let img=doc.page(at:pageIndex)!.thumbnail(of:NSSize(width:1200,height:1600),for:.mediaBox)
 let rep=NSBitmapImageRep(data:img.tiffRepresentation!)!
 let imageName=name+"-checked-figure.png"
 try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:base+"/"+imageName))
 records.append(["report":name,"pages":doc.pageCount,"renderedPage":pageIndex+1,"extractedCharacters":text.count,"renderedFile":imageName])
}
let data=try JSONSerialization.data(withJSONObject:records,options:[.prettyPrinted,.sortedKeys])
try data.write(to:URL(fileURLWithPath:base+"/pdf-inspection.json"))
print(String(data:data,encoding:.utf8)!)
