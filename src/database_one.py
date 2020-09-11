import time
import csv
import hashlib

file_name = "blockchain_database_1.csv"
def return_previous_hash():
	try:
		with open(file_name , 'r') as csv_file:
			csv_reader = csv.reader(csv_file)
			datas = [row for row in csv_reader]
			data = datas[len(datas)-1]
			return get_hash(data[1])
	except:
		return "0000"


def get_hash(*args):
	temp = ''
	for arg in args:
		temp += str(arg)

	return hashlib.sha256(temp.encode('utf-8')).hexdigest()

def check_consistency():
	try:
		with open(file_name , 'r') as f:
			csv_reader = csv.reader(f)
			previous_hash = "0000"
			for row in csv_reader:
				if previous_hash != row[len(row)-1]:
					print("file corrupted")

					print(f"hash of Data {previous_data} does not match with {row[len(row)-1]}")
					print("file corrupted")
					raise SystemExit
				previous_hash = get_hash(row[1])
				previous_data = row[1]
			print("consistency check passed..!")
	except FileNotFoundError:
		print("file not found:")

 
def write_to_csv(*args):
	with open(file_name , 'a') as csv_file:
		csv_reader = csv.writer(csv_file)
		csv_reader.writerow(args)



class Object:
	def __init__(self , data , prev_hash , time_stamp):
		self.data = data
		self.previous_hash = prev_hash
		self.time_stamp = time_stamp
	
	def show_data(self):
		print(f"Hash:{self.__hash__()}\nTime Stamp:{time.ctime((self.time_stamp))}\nData:{self.data}\nPrevious Hash:{self.previous_hash}")	

	def __hash__(self):
		return get_hash([self.data , self.previous_hash , self.time_stamp])


def add_data(previous_hash):
	data = input("Enter data value:")
	time_stamp = time.time()
	obj  = Object(data , previous_hash , time_stamp)
	write_to_csv(obj.__hash__() , [data , previous_hash , time_stamp] , previous_hash)
	obj.show_data()
	return obj.__hash__()

if __name__ == '__main__':
	previous_hash = return_previous_hash()
	try:
		while True:
			print("1)Make Entry\n2)Exit:")
			choice = input("Enter process to continue with:")
			if choice == "2":
				break
			previous_hash = add_data(previous_hash)
			check_consistency()
	except SystemExit:
		print(":::::::HASH MISMATCHED:::::::::")