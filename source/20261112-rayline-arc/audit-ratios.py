import statistics
rows = [('DeepSWE', 69.9, 72.3, 1.1), ('Terminal-Bench 2.1', 90.7, 90.5, 75.7), ('SWE-Atlas QA', 61.6, 62.6, 1.6), ('Tau3 Banking', 42.8, 35.3, 17.3), ('GPQA Diamond', 89.5, 92.5, 12.3), ('MMMU-Pro Vision', 82.2, 82.7, 40.9)]
quality=statistics.mean(a/b*100 for _,b,a,_ in rows)
print("macro quality %",quality)
print("naive macro cost %",statistics.mean(c for *_,c in rows))
assert abs(quality-98.54553486318457)<1e-9
