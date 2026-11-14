fn value() -> u32 { 1 }
fn main() { for i in 0..32 { println!("state={} value={}", i, value()); std::thread::sleep(std::time::Duration::from_millis(250)); } }
#[test] fn addition() { assert_eq!(2 + 3, 5); }
#[test] fn vec_sum() { let v = vec![1u32, 2, 3]; assert_eq!(v.iter().sum::<u32>(), 6); }
