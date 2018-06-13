import os
import re
import operator
import subprocess

root = "/mnt/students"

cmd = "Rscript class/BME230_F1score_V2.R /mnt/students/{}/predict.tsv /mnt/data/tcga_mutation_test_labels.tsv"

leaderboard = {}

for id in os.listdir(root):
    if os.path.exists(os.path.join(root, id, "predict.tsv")):
	leaderboard[id] = {}
	print("Ranking {}".format(id))
	try:
	    scores = subprocess.check_output(cmd.format(id).split(" "))
        except subprocess.CalledProcessError as e:
	    print("Problems ranking {}: {}".format(id, e.output))
	leaderboard[id]["Tissue"] = float(re.findall("Tissue F1 score: (NaN|[0-9]*\.?[0-9]*)", scores)[0])
	leaderboard[id]["TP53"] = float(re.findall("TP53_F1_score: (NaN|[0-9]*\.?[0-9]*)", scores)[0])
	leaderboard[id]["KRAS"] = float(re.findall("KRAS_F1_score: (NaN|[0-9]*\.?[0-9]*)", scores)[0])
	leaderboard[id]["BRAF"] = float(re.findall("BRAF_F1_score: (NaN|[0-9]*\.?[0-9]*)", scores)[0])
	leaderboard[id]["Mutation"] = float(re.findall("Mutation_F1_score: (NaN|[0-9]*\.?[0-9]*)", scores)[0])
	leaderboard[id]["Overall"] = float(re.findall("Final_F1_score: (NaN|[0-9]*\.?[0-9]*)", scores)[0])

for id in sorted(leaderboard.keys(), key=lambda x: leaderboard[x]["Overall"], reverse=True):
    print(id)
    print("Overall: {:.6f}".format(leaderboard[id]["Overall"]))
    print("Tissue: {:.6f}".format(leaderboard[id]["Tissue"]))
    print("TP53: {:.6f}".format(leaderboard[id]["TP53"]))
    print("KRAS: {:.6f}".format(leaderboard[id]["KRAS"]))
    print("BRAF: {:.6f}".format(leaderboard[id]["BRAF"]))
    print("Mutation: {:.6f}".format(leaderboard[id]["Mutation"]))
    print("")
