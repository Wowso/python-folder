import csv

def save_to_file(title, jobs):
    file = open(f"{title}.csv", "w",-1,"utf-8")
    writer = csv.writer(file)
    writer.writerow(["Title","Company","Link"])

    for job in jobs:
        writer.writerow(list(job.values()))

    print(f"{title}.csv Compleate")

    return