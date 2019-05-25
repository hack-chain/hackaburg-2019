import urllib.request
from collections import Counter
import json
import umap
import subprocess

class Predictor():
    def json_to_array(self, data):
        nontracker_cookies = [
            ".bing.com",
            ".c.bing.com",
            "g.alicdn.com",
            "bat.bing.com",
            "c.bing.com",
            ".slickdeals.net",
            "sp.auth.adobe.com",
            ".google.com"
        ]
                
        tracker_cookies = [
            ".rubiconproject.com",
            ".pubmatic.com",
            ".casalemedia.com",
            ".mookie1.com",
            ".adnxs.com",
            ".doubleclick.net",
            ".scorecardresearch.com",
            ".w55c.net",
            ".bluekai.com",
            ".bidswitch.net",
            ".advertising.com",
            ".adsrvr.org",
            "ads.stickyadstv.com",
            ".linkedin.com",
            ".crwdcntrl.net",
            ".smartadserver.com",
        ]

        trackers = [
            "www.google-analytics.com",
            "cm.g.doubleclick.net",
            "googleads.g.doubleclick.net",
            "www.google.com",
            "adservice.google.com",
            "ib.adnxs.com",
            "www.facebook.com",
            "sb.scorecardresearch.com",
            "securepubads.g.doubleclick.net",
            "stats.g.doubleclick.net",
        ]

        third_parties = [
            "www.google-analytics.com",
            "cm.g.doubleclick.net",
            "googleads.g.doubleclick.net",
            "www.google.com",
            "adservice.google.com",
            "ib.adnxs.com",
            "www.facebook.com",
            "sb.scorecardresearch.com",
            "securepubads.g.doubleclick.net",
            "stats.g.doubleclick.net",
        ]   

        result = []
        data_cookies = [x["domain"] for x in data["cookies"]]
        for c in tracker_cookies + nontracker_cookies:
            if c in data_cookies:
                result.append(1)
            else:
                result.append(0)
    
        result.append(data["cookiestats"]["first_party_long"])
        result.append(data["cookiestats"]["first_party_short"])

        result.append(data["cookiestats"]["third_party_long"])
        result.append(data["cookiestats"]["third_party_short"])
            
        for t in trackers:
            if t in data["tracking"]["trackers"]:
                result.append(1)
            else:
                result.append(0)
        
        result.append(data["tracking"]["num_tracker_requests"])
        result.append(data["tracking"]["num_tracker_cookies"])
            
        for tp in third_parties:
            if tp in data["third_parties"]["fqdns"]:
                result.append(1)
            else:
                result.append(0)
        result.append(data["third_parties"]["num_http_requests"] + data["third_parties"]["num_https_requests"])
        if data["fingerprinting"]["canvas"]["is_fingerprinting"]:
            result.append(1)
        else:
            result.append(0)
        result.append(data["tracking"]["num_tracker_requests"])
        result.append(data["tracking"]["num_tracker_cookies"])
            
        for tp in third_parties:
            if tp in data["third_parties"]["fqdns"]:
                result.append(1)
            else:
                result.append(0)
        result.append(data["third_parties"]["num_http_requests"] + data["third_parties"]["num_https_requests"])
        if data["fingerprinting"]["canvas"]["is_fingerprinting"]:
            result.append(1)
        else:
            result.append(0)
            
        return result
        
    def json_to_xy(self, data):
        return self.reducer.transform([self.json_to_array(data)])

    def json_to_score(self, data):
        def count_tracker_cookies():
            count = 0
            for cookie in data["cookies"]:
                if cookie["is_thirdparty"] and cookie["is_tracker"]:
                    count += 1
            return count

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

        return -0.1 * count_tracker_cookies() - 1 * count_ga() - 10 * count_fingerprinting()

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


    def __init__(self):
        url = "https://gist.githubusercontent.com/m-malikov/352e6c0ffa222e25f30d223419b92f89/raw/f3138771ddaf128e5d91817be5618decde8d64f7/tracker_data.json"
        self.data = {}

        with urllib.request.urlopen(url) as file:
            self.data = json.loads(file.read().decode())

        self.vectorized_data = []
        for hostname in self.data:
            self.vectorized_data.append(self.json_to_array(self.data[hostname]))
        self.reducer = umap.UMAP(n_neighbors=25, min_dist = 0.2)
        self.reducer.fit(self.vectorized_data)

        self.final_data = {}
        for hostname in self.data:
            x, y = self.json_to_xy(self.data[hostname])[0]
            score = self.json_to_score(self.data[hostname])

            self.final_data[hostname] = {
                "x": float(x),
                "y": float(y),
                "score": float(score)
            }



        


        
        

        






