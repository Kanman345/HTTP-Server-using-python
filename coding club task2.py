from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs


file_path = 'ids.txt'

year_mapping = { 
    "1" : "2024",
    "2" : "2023",
    "3" : "2022",
    "4" : "2021",
    "5" : "2020"
}

campus_mapping = {
    "P" : "pilani",
    "G" : "goa",
    "H" : "hyderabad"
}

branch_mapping = {
    "cs" : "A7",
    "ece" : "AA",
    "eee" : "A3",
    "eni" : "A8",
    "mech" : "A4",
    "civil" : "A2",
    "chemical" : "A1",
    "phy" : "B5",
    "chem" : "B2", 
    "math" : "B4",
    "bio" : "B1",
    "eco" : "B3",
    "pharma" : "A5",
    "manu" : "AB",
    "genstudies" : "D2"
} 

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:

            parsed_path = urlparse(self.path)
            path_segments = parsed_path.path.strip("/").split("/")

            query_components = parse_qs(urlparse(self.path).query)
            year_value = query_components.get("year", [None])[0] 
            format_value = query_components.get("format", [None])[0] 
            branch_value = query_components.get("branch", [None])[0]

            with open(file_path, 'r') as file:
                ids = file.readlines()  

            ids = [id.strip() for id in ids]

            if branch_value and branch_value in branch_mapping:
                branch_value2 = branch_mapping[branch_value]
                ids = [id for id in ids if branch_value2 in id]

            
            if year_value and year_value in year_mapping:
                filter_value = year_mapping[year_value]
                ids = [id for id in ids if filter_value in id]

            matched_id = None
            if len(path_segments) == 1 and path_segments[0]:
                user_id = path_segments[0]  

                reverse_branch_mapping = {v: k for k, v in branch_mapping.items()}

                for id in ids:
                    if user_id in id:
                        matched_id = id
                        break

                if matched_id:

                    campus_letter = matched_id[-1]
                    campus = campus_mapping[campus_letter]
                    
                    year = matched_id[:4]

                    branch_code = matched_id[4:6]
                    branch = reverse_branch_mapping[branch_code]


                
                    ids = {
                        "id": matched_id,
                        "uid": user_id,  
                        "email": f"{matched_id}@{campus}.bits-pilani.ac.in",  
                        "branch": branch,  
                        "year": year,  
                        "campus": campus  
                    }
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    error_response = {
                        "error": "ID not found",
                        "status code": 404
                    }
                    self.wfile.write(json.dumps(error_response, indent=4).encode('utf-8'))
                    return     

            
            if format_value == 'text':
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write('\n'.join(ids).encode('utf-8'))  # Send the raw file contents

            else:
                
                response = {
                    'IDS': ids           
                }
                response_json = json.dumps(response, indent=4)


                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                # Write the JSON response to the HTTP response body
                self.wfile.write(response_json.encode('utf-8'))

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found")


server_address = ('', 6969)  
httpd = HTTPServer(server_address, HTTPRequestHandler)

print("Serving on port 6969")
httpd.serve_forever()
