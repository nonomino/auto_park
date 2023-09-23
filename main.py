import mysql.connector
import datetime, sys, re, time
from PyQt5 import QtCore, QtWidgets, uic

db_connection = mysql.connector.connect(
	host="localhost", user="smoke", passwd="hellomoto", database="car", autocommit=True
)
db_cursor = db_connection.cursor()

db_cursor.execute("DROP TABLE IF EXISTS slot, duration, entry, exits, cost")
db_cursor.execute("CREATE TABLE slot (carNumber VARCHAR(15), slot int)")
db_cursor.execute("CREATE TABLE entry (carNumber VARCHAR(15), entry VARCHAR(40))")
db_cursor.execute("CREATE TABLE exits (carNumber VARCHAR(15), exit1 VARCHAR(40))")
db_cursor.execute("CREATE TABLE duration (carNumber VARCHAR(15), durationInSec int)")
db_cursor.execute("CREATE TABLE cost (carNumber VARCHAR(15), cost int)")

parking_slots = [False for _ in range(16)]


class ParkingSystemUI(QtWidgets.QMainWindow):
	def __init__(self):
		super(ParkingSystemUI, self).__init__()
		uic.loadUi("front.ui", self)
		self.entry_button.released.connect(self.handle_entry)
		self.exit_button.released.connect(self.handle_exit)

	def handle_entry(self):
		car_number = self.car_number_input.text()
		if car_number and not self.is_car_already_parked(car_number):
			parking_slot = self.assign_parking_slot()
			self.update_ui_for_parking_slot(parking_slot)
			self.record_entry(car_number, parking_slot)
		else:
			self.display_error_message("Duplicate or Invalid")

	def handle_exit(self):
		car_number = self.car_number_input.text()
		if car_number and self.is_car_already_parked(car_number):
			parking_slot, entry_time = self.get_parking_slot_and_entry_time(car_number)
			exit_time = datetime.datetime.now()
			parking_duration = (exit_time - entry_time).total_seconds()
			parking_cost = min(int(parking_duration * 10), 150)
			self.display_cost(parking_cost)
			self.free_parking_slot(parking_slot)
			self.record_exit_and_duration(car_number, exit_time, parking_duration, parking_cost)
			self.update_ui_for_parking_slot(parking_slot, is_exit=True)
		else:
			self.display_error_message("Invalid Entry")

	def is_car_already_parked(self, car_number):
		db_cursor.execute("SELECT carNumber FROM slot")
		parked_cars = [record[0] for record in db_cursor.fetchall()]
		return car_number in parked_cars

	def assign_parking_slot(self):
		available_slot = parking_slots.index(False)
		parking_slots[available_slot] = True
		return available_slot + 1

	def update_ui_for_parking_slot(self, parking_slot, is_exit=False):
		slot_button = getattr(self, f"s{parking_slot}")
		slot_button.setStyleSheet("background-color: #40FF50" if is_exit else "background-color: #FF0B00")

	def record_entry(self, car_number, parking_slot):
		entry_time = datetime.datetime.now()
		db_cursor.execute("INSERT INTO slot (carNumber, slot) VALUES (%s, %s)", (car_number, parking_slot))
		db_cursor.execute("INSERT INTO entry (carNumber, entry) VALUES (%s, %s)", (car_number, entry_time))

	def free_parking_slot(self, parking_slot):
		parking_slots[parking_slot - 1] = False

	def get_parking_slot_and_entry_time(self, car_number):
		db_cursor.execute("SELECT slot FROM slot WHERE carNumber = %s", (car_number,))
		parking_slot = int(re.sub("[^0-9]", "", str(db_cursor.fetchone())))
		db_cursor.execute("SELECT entry FROM entry WHERE carNumber = %s", (car_number,))
		entry_time = datetime.datetime.fromisoformat(re.sub('[,)(/\']', '', str(db_cursor.fetchone())))
		return parking_slot, entry_time

	def record_exit_and_duration(self, car_number, exit_time, duration, cost):
		db_cursor.execute("UPDATE exits SET exit1 = %s WHERE carNumber = %s", (exit_time, car_number))
		db_cursor.execute("UPDATE duration SET durationInSec = %s WHERE carNumber = %s", (duration, car_number))
		db_cursor.execute("UPDATE cost SET cost = %s WHERE carNumber = %s", (cost, car_number))

	def display_cost(self, cost):
		self.label_2.setText(f"Cost: Rs. {cost}")

	def display_error_message(self, message):
		self.label_2.setText(message)


def main():
	app = QtWidgets.QApplication(sys.argv)
	window = ParkingSystemUI()
	window.show()
	app.exec_()


if __name__ == "__main__":
	main()