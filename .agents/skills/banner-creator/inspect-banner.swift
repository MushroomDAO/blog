#!/usr/bin/env swift
// inspect-banner.swift — macOS Vision: detect rendered text + human faces in a banner.
// Usage: swift inspect-banner.swift <image-path>
// Prints JSON: {"faces":N,"texts":[{"s":"...","c":0.93}, ...]}
import Vision
import Foundation
import AppKit

guard CommandLine.arguments.count > 1 else {
    fputs("Usage: swift inspect-banner.swift <image-path>\n", stderr); exit(2)
}
let path = CommandLine.arguments[1]
guard let image = NSImage(contentsOfFile: path),
      let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    fputs("Error: cannot load image \(path)\n", stderr); exit(2)
}

var texts: [(String, Float)] = []
var faces = 0

let textReq = VNRecognizeTextRequest { req, _ in
    guard let obs = req.results as? [VNRecognizedTextObservation] else { return }
    for o in obs {
        if let c = o.topCandidates(1).first { texts.append((c.string, c.confidence)) }
    }
}
textReq.recognitionLevel = .accurate
textReq.usesLanguageCorrection = false

let faceReq = VNDetectFaceRectanglesRequest { req, _ in
    faces = (req.results as? [VNFaceObservation])?.count ?? 0
}

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do { try handler.perform([textReq, faceReq]) }
catch { fputs("Vision error: \(error)\n", stderr); exit(2) }

func esc(_ s: String) -> String {
    var o = ""
    for ch in s.unicodeScalars {
        switch ch {
        case "\"": o += "\\\""
        case "\\": o += "\\\\"
        case "\n", "\r", "\t": o += " "
        default:
            if ch.value < 0x20 { o += " " } else { o.unicodeScalars.append(ch) }
        }
    }
    return o
}

let items = texts.map { "{\"s\":\"\(esc($0.0))\",\"c\":\(String(format: "%.3f", $0.1))}" }
print("{\"faces\":\(faces),\"texts\":[\(items.joined(separator: ","))]}")
