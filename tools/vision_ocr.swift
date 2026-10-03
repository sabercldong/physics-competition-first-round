import AppKit
import Foundation
import Vision

guard CommandLine.arguments.count == 3 else {
    fputs("usage: vision_ocr IMAGE OUTPUT\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])

guard
    let image = NSImage(contentsOf: inputURL),
    let tiff = image.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiff),
    let cgImage = bitmap.cgImage
else {
    fputs("cannot read image\n", stderr)
    exit(3)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.minimumTextHeight = 0.008

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try handler.perform([request])

let observations = (request.results ?? []).sorted { lhs, rhs in
    let dy = lhs.boundingBox.midY - rhs.boundingBox.midY
    if abs(dy) > 0.012 { return dy > 0 }
    return lhs.boundingBox.minX < rhs.boundingBox.minX
}

let lines = observations.compactMap { observation -> String? in
    guard let candidate = observation.topCandidates(1).first else { return nil }
    let box = observation.boundingBox
    return String(
        format: "%.5f\t%.5f\t%.5f\t%.5f\t%@",
        box.minX,
        box.minY,
        box.width,
        box.height,
        candidate.string.replacingOccurrences(of: "\t", with: " ")
    )
}

try (lines.joined(separator: "\n") + "\n").write(
    to: outputURL,
    atomically: true,
    encoding: .utf8
)
