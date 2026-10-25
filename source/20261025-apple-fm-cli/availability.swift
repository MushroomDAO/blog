import Foundation
import FoundationModels
let model = SystemLanguageModel.default
print("OS: \(ProcessInfo.processInfo.operatingSystemVersionString)")
print("Availability: \(model.availability)")
print("Available: \(model.isAvailable)")
