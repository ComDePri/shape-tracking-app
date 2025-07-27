import datetime
import json
import time
import requests

BUCKET_NAME = 'shape-dependent-tracking-2025'
META_DATA_FORMAT = """
    "pid": "{}",
    "exp": "shape-dependent-tracking-2025",
    "start_time": "{}",
    "data": ["""

NEW_SECTION_FORMAT = """
            "trial_num": "{}",
            "trial_info": "{}",
            "data" : [ 
"""

class DataHandler():

    def __init__(self, pid: str, output_file: str, s3_flag: bool = False):
        self.pid = pid
        self.start_time = str(datetime.datetime.now())
        self.buffer = []
        self.output_file = output_file
        self.output_stream = open(output_file, 'w', encoding='utf-8')
        self.section_num = 0
        self.__write_metadata()
        self.s3_flag = s3_flag

    def start_new_section(self, info, first=False):
        if not first:
            self.__close_section()
        self.buffer = []
        self.output_stream.write("\n\t\t{" + NEW_SECTION_FORMAT.format(self.section_num, info))
        self.section_num += 1


    def write_data(self, data):
        """
        write data to file
        """
        print(data)
        self.buffer.append(data)

        if len(self.buffer) > 10:
            self.__flush_buffer()

    def close_file(self):
        self.__flush_buffer()
        self.__handle_closing_text()
        self.output_stream.close()
        if self.s3_flag:
            self.upload_data()
        self.buffer = []

    def __flush_buffer(self):
        """
        flush the buffer to file and start new buffer
        """
        if len(self.buffer) > 0:
            sep = ',\n' + '\t'*4
            # Join the buffer items into a string if it's a list of items.
            content = '\t'*4 + sep.join(str(item) for item in self.buffer) + ',\n'

            # Write the content to the file without the brackets
            self.output_stream.write(content.replace("'", '"'))
            self.output_stream.flush()

            # Clear the buffer
            self.buffer = []

    def clear_buffer(self):
        """
        clear the buffer
        """
        self.buffer = []

    def __write_metadata(self):
        data = "{" + META_DATA_FORMAT.format(self.pid, self.start_time)
        self.output_stream.write(data)

    def __close_section(self):
        self.__flush_buffer()
        self.output_stream.seek(self.output_stream.tell() - 3, 0)
        self.output_stream.truncate()
        self.output_stream.write("\n\t\t\t]\n\t\t},")

    def __read_file(self):
        """
        read data from file
        """
        with open(self.output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data


    def __handle_closing_text(self):
        self.__close_section()
        self.output_stream.seek(self.output_stream.tell() -3, 0)
        self.output_stream.truncate()
        self.output_stream.write("\t}\n\t]\n}")

    def __read_file_as_json_string(self):
        try:
            with open(self.output_file, 'r') as file:
                # Read the content of the file
                file_content = file.read()
                # Convert to a JSON-encoded string
                return json.dumps(file_content)
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def __do_upload_data(self):
        """
        recursive call for uploading data
        """

        url = 'https://hss74dd1ed.execute-api.us-east-1.amazonaws.com/dev/'
        headers = {
            'Content-Type': 'application/json',  # Matches `contentType` in JavaScript
            'User-Agent': 'Mozilla/5.0',  # Optional: Mimics browser behavior
            'Accept': 'application/json',  # Optional: Indicates expected response type
        }

        data = {
            "subject_id": str(self.pid),
            "bucket": BUCKET_NAME,
            "exp_data": self.__read_file_as_json_string(),  # Ensure the data is JSON-stringified
        }

        response = requests.post(
            url,
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            print("Data uploaded successfully! Clicking OK will close the experiment.")
            # Simulate closing the experiment or redirect here
        else:
            print("Failed to upload data.")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            raise requests.exceptions.RequestException

    def upload_data(self):
        """
        upload data to s3
        """
        retries = 0
        max_retries = 5
        backoff_factor = 2  # Exponential backoff multiplier

        while retries < max_retries:
            try:
                self.__do_upload_data()
                return  # Exit the loop if upload is successful
            except requests.exceptions.RequestException as e:
                retries += 1
                wait_time = backoff_factor ** retries  # Exponential backoff
                print(f"Upload failed. Attempt {retries}/{max_retries}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        print("Max retries reached. Upload failed.")