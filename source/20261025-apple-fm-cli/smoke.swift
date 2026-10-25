import Foundation
import FoundationModels
@main struct Smoke {
  static func main() async {
    let model = SystemLanguageModel.default
    let prompt = "请用一句简体中文解释什么是 AI Agent。"
    do {
      guard model.isAvailable else {
        print("Model unavailable: \(model.availability)")
        exit(2)
      }
      let session = LanguageModelSession(model: model)
      let response = try await session.respond(to: prompt)
      let result: [String: Any] = ["backend": "SystemLanguageModel.default", "os": ProcessInfo.processInfo.operatingSystemVersionString, "prompt": prompt, "response": response.content, "scope": "One functional generation via Swift on macOS 26; not the macOS 27 fm CLI or a benchmark"]
      let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes])
      print(String(decoding: data, as: UTF8.self))
    } catch {
      print("Generation error: \(error)")
      exit(1)
    }
  }
}
