#!/usr/bin/env swift
// ocr-image.swift — macOS Vision framework OCR
// 用法: swift ocr-image.swift image.jpg
import Vision
import Foundation
import AppKit

guard CommandLine.arguments.count > 1 else {
    fputs("Usage: swift ocr-image.swift <image-path>\n", stderr)
    exit(1)
}

let imagePath = CommandLine.arguments[1]
guard let image = NSImage(contentsOfFile: imagePath),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    fputs("Error: cannot load image \(imagePath)\n", stderr)
    exit(1)
}

let semaphore = DispatchSemaphore(value: 0)
var results: [String] = []

let request = VNRecognizeTextRequest { req, err in
    defer { semaphore.signal() }
    if let err = err { fputs("OCR error: \(err)\n", stderr); return }
    guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
    for obs in observations {
        if let candidate = obs.topCandidates(1).first {
            results.append(candidate.string)
        }
    }
}
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
    semaphore.wait()
    print(results.joined(separator: "\n"))
} catch {
    fputs("Error: \(error)\n", stderr)
    exit(1)
}
