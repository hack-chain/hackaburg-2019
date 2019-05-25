import urllib.request
from collections import Counter
import json
import umap
import subprocess
import math
import random

class Predictor():
    def json_to_array(self, data):
        result = []
        data_cookies = [x["domain"] for x in data["cookies"]]
        for c in self.tracker_cookies + self.nontracker_cookies:
            if c in data_cookies:
                result.append(1)
            else:
                result.append(0)
    
        result.append(data["cookiestats"]["first_party_long"])
        result.append(data["cookiestats"]["first_party_short"])

        result.append(data["cookiestats"]["third_party_long"])
        result.append(data["cookiestats"]["third_party_short"])
            
        for t in self.trackers:
            if t in data["tracking"]["trackers"]:
                result.append(1)
            else:
                result.append(0)
        
        result.append(data["tracking"]["num_tracker_requests"])
        result.append(data["tracking"]["num_tracker_cookies"])
            
        for tp in self.third_parties:
            if tp in data["third_parties"]["fqdns"]:
                result.append(1)
            else:
                result.append(0)
        result.append(data["third_parties"]["num_http_requests"] + data["third_parties"]["num_https_requests"])
        try:
            if data["fingerprinting"]["canvas"]["is_fingerprinting"]:
                result.append(1)
            else:
                result.append(0)
        except:
            result.append(0)

        return result
        
    def json_to_xy(self, data):
        return self.reducer.transform([self.json_to_array(data)])

    def json_to_score(self, data):
        def count_tracker_cookies():
            count = 0
            for cookie in data.get("cookies", []):
                if cookie["is_thirdparty"] and cookie["is_tracker"]:
                    count += 1
            return count

        def count_nontracker_cookies():
            count = 0
            for cookie in data["cookies"]:
                if (not cookie["is_thirdparty"]) and cookie["is_tracker"]:
                    count += 1
            return count
        
        def count_trackers():
            return 3 * len(data["tracking"]["trackers"]) + \
                    data["tracking"]["num_tracker_requests"] + \
                    data["tracking"]["num_tracker_cookies"]
        
        def count_thirdparty():
            return 3 * len(data["third_parties"]["fqdns"]) + \
                    data["third_parties"]["num_http_requests"] + \
                    data["third_parties"]["num_https_requests"]

        def count_fingerprinting():
            count = 0
            if "fingerprinting" in data:
                if data["fingerprinting"]["canvas"]["is_fingerprinting"]:
                    count = 1
            return count
        
        def count_ga():
            count = 0
            if "trakcers" in data["google_analytics"]:
                for obj in data["google_analytics"]["trackers"]:
                    if not obj["anonymize_ip"]:
                        count += 1
            return count

        score = 1 * count_tracker_cookies() + 10 * count_ga() + 1000 * count_fingerprinting() + count_thirdparty() + 0.2 * count_nontracker_cookies() + 2 * count_trackers()
        return -2 * math.log(score + 1)

    def predict(self, hostname):
        data = subprocess.check_output(["privacyscanner", "scan", "https://" + hostname])
        data = data.decode("utf-8")
        data = json.loads(data)
        x, y = self.json_to_xy(data)[0]
        score = self.json_to_score(data)
        return {
            "x": float(x),
            "y": float(y),
            "score": float(score)
        }

    def get_most_common(self, array, n=30):
        return list(map(lambda x: x[0], Counter(array).most_common(n)))

    def __init__(self):
        with open("data.json") as f:
            data = json.loads(f.read())

        cookie_domains = [[], []]

        for hostname in data:
            for cookie in data[hostname]["cookies"]:
                if cookie["is_thirdparty"]:
                    tracker_index = 1 if cookie["is_tracker"] else 0
                    cookie_domains[tracker_index].append(cookie["domain"])

        self.nontracker_cookies = self.get_most_common(cookie_domains[1])
        self.tracker_cookies = self.get_most_common(cookie_domains[1])

        trackers = []
        for hostname in data:
            trackers += data[hostname]["tracking"]["trackers"]
        self.trackers = self.get_most_common(trackers)

        third_parties = []
        for hostname in data:
            third_parties += data[hostname]["third_parties"]["fqdns"]
        self.third_parties = self.get_most_common(third_parties)

        self.vectorized_data = []
        for hostname in data:
            self.vectorized_data.append(self.json_to_array(data[hostname]))
        self.reducer = umap.UMAP(n_neighbors=30, min_dist = 0.3, random_state=2)
        self.reducer.fit(self.vectorized_data)

        self.final_data = {}
        for hostname in data:
            x, y = self.json_to_xy(data[hostname])[0]
            score = self.json_to_score(data[hostname])

            self.final_data[hostname] = {
                "x": float(x),
                "y": float(y),
                "score": float(score) + random.random() - 1
            }



        


        
        

        






