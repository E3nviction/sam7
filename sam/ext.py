from io import TextIOWrapper
from typing import Any
import re


def error(msg: str) -> None:
	print("\033[91m" + msg + "\033[0m")
	exit(1)


char_list = {
	1: ' ', 2: '!', 3: '"', 4: '#', 5: '$', 6: '%', 7: '&', 8: "'", 9: '(', 10: ')', 11: '*', 12: '+', 13: ',', 14: '-', 15: '.', 16: '/', 17: '0', 18: '1', 19: '2', 20: '3', 21: '4', 22: '5', 23: '6', 24: '7', 25: '8', 26: '9', 27: ':', 28: ';', 29: '<', 30: '=', 31: '>', 32: '?', 33: '@', 34: 'A', 35: 'B', 36: 'C', 37: 'D', 38: 'E', 39: 'F', 40: 'G', 41: 'H', 42: 'I', 43: 'J', 44: 'K', 45: 'L', 46: 'M', 47: 'N', 48: 'O', 49: 'P', 50: 'Q', 51: 'R', 52: 'S', 53: 'T', 54: 'U', 55: 'V', 56: 'W', 57: 'X', 58: 'Y', 59: 'Z', 60: '[', 61: '\\', 62: ']', 63: '^', 64: '_', 65: '`', 66: 'a', 67: 'b', 68: 'c', 69: 'd', 70: 'e', 71: 'f', 72: 'g', 73: 'h', 74: 'i', 75: 'j', 76: 'k', 77: 'l', 78: 'm', 79: 'n', 80: 'o', 81: 'p', 82: 'q', 83: 'r', 84: 's', 85: 't', 86: 'u', 87: 'v', 88: 'w', 89: 'x', 90: 'y', 91: 'z', 92: '{', 93: '|', 94: '}', 95: '~', 96: ""}
#print({i-31: chr(i) for i in range(32, 127)})


class SamValue:
	def __init__(self, value: Any, type: str = "def", name: str = "Number", *args, **kwargs) -> None:
		if value.startswith("$"):
			type = "address"
		elif value.startswith('"') and value.endswith('"'):
			type = "char"
		else:
			type = "int"
		self.type = type
		self.value = value
		self.name = name

		self.args = args
		self.kwargs = kwargs

		if self.type == "int":
			self.value = self.value.rjust(8, '0')
			if not re.match(r"^[01]{8}$", self.value):
				error(
					f"Fatal Error | Invalid value '{value}' for register '{name}'")
		if self.type == "address":
			self.value = self.value[1:]
			if not re.match(r"^[01]{3}$", self.value):
				error(
					f"Fatal Error | Invalid value '{value}' for memory address")
		if self.type == "char":
			if len(self.value) < 3 or len(self.value) > 3:
				error(f"Fatal Error | Invalid value '{value}' for char")
			if self.value.startswith('"') and self.value.endswith('"'):
				self.value = self.value[1:-1][0]
			if not re.match(r"^.$", self.value):
				error(f"Fatal Error | Invalid value '{value}' for char")
			# use charlist
			if self.value not in char_list.values():
				error(f"Fatal Error | Invalid value '{value}' for char")
			self.value = str([k for k, v in char_list.items() if v == self.value][0])

	def __str__(self) -> str:
		return f"{self.type}({self.value})"


class SamExt:
	def __init__(self) -> None:
		self.data = []
		self.registers = {
			"A":  SamValue("00000000"),
			"B":  SamValue("00000000"),
			"C":  SamValue("00000000"),
			"X":  SamValue("00000000"),
			"E":  SamValue("00000000"),
			"ZZ": SamValue("00000000")
		}
		self.memory = {num: SamValue("00000000") for num in range(64)}
		self.running = False
		self.pce = 0
		self.syscall_old = ""
		self.zz_stack = []
		self.labels = {}

	def get_abs_value(self, value: SamValue) -> SamValue:
		if value.type == "address":
			return self.memory[int(value.value, 2)]
		return value

	def set_reg(self, reg: str, value: SamValue) -> None:
		value = self.get_abs_value(value)
		if reg not in self.registers:
			error(f"Fatal Error | pce {self.pce} | Invalid register '{reg}'")
		self.registers[reg] = value

	def set_mem(self, num: SamValue, value: SamValue) -> None:
		value = self.get_abs_value(value)
		if int(num.value, 2) not in self.memory:
			error(
				f"Fatal Error | pce {self.pce} | Invalid memory address '{int(num.value, 2)}'")
		self.memory[int(num.value, 2)] = value

	def connect(self, f: TextIOWrapper) -> None:
		self.data = f.readlines()

	def get_line(self) -> str:
		return self.data[self.pce].strip()

	def index_labels(self) -> None:
		for i, line in enumerate(self.data):
			line = line.strip()
			if line.startswith("//"):
				continue
			if not line:
				continue
			if line.startswith("."):
				label = line.split(" ")[0]
				if label in self.labels:
					error(
						f"Fatal Error | pce {self.pce} | Label '{label}' already defined")
				self.labels[label] = i

	def run(self, verbose: bool = False) -> None:
		self.running = True
		self.pce = 0
		if verbose:
			print("Indexing labels...")
		self.index_labels()
		if verbose:
			print(f"Found {len(self.labels)} labels.")
		if verbose:
			print("Running...\n")
		while self.running:
			if self.pce >= len(self.data):
				break
			line = self.get_line()
			self.pce += 1

			# cut away comments
			line = line.split("//")[0].strip()

			if not line:
				continue

			if line.startswith("LDI"):  # Load Immediate
				line = line.split(" ")
				if len(line) != 3:
					error(
						f"Fatal Error | pce {self.pce} | LDI: Invalid instruction '{'·'.join(line)}'")
				self.set_reg(line[1], SamValue(line[2]))
			elif line.startswith("LTM"):  # Load To Memory
				line = line.split(" ")
				if len(line) != 3:
					error(
						f"Fatal Error | pce {self.pce} | LTM: Invalid instruction '{'·'.join(line)}'")
				self.set_mem(SamValue(line[1]), SamValue(line[2]))
			elif line.startswith("BRK"):  # Break
				line = line.split(" ")
				if len(line) != 1:
					error(
						f"Fatal Error | pce {self.pce} | BRK: Invalid instruction '{'·'.join(line)}'")
				self.running = False
			elif line.startswith("BN"):  # Branch
				line = line.split(" ")
				if len(line) != 2:
					error(
						f"Fatal Error | pce {self.pce} | BN: Invalid instruction '{'·'.join(line)}'")
				self.pce = self.labels[line[1]]
			elif line.startswith("CMP"):  # Compare
				line = line.split(" ")
				if len(line) != 2:
					error(
						f"Fatal Error | pce {self.pce} | CMP: Invalid instruction '{'·'.join(line)}'")
				self.compare(line[1])
			elif line.startswith("RTM"):  # Register To Memory
				line = line.split(" ")
				if len(line) != 3:
					error(
						f"Fatal Error | pce {self.pce} | RTM: Invalid instruction '{'·'.join(line)}'")
				self.set_mem(SamValue(line[1]), self.registers[line[2]])
			elif line.startswith("BIF"):  # Branch If
				line = line.split(" ")
				if len(line) != 2:
					error(
						f"Fatal Error | pce {self.pce} | BIF: Invalid instruction '{'·'.join(line)}'")
				if self.registers["C"].value == SamValue("00000001").value:
					self.pce = self.labels[line[1]]
			elif line.startswith("."):  # Label
				pass
			else:
				line = line.split(" ")
				error(
					f"Fatal Error | pce {self.pce} | Invalid instruction '{'·'.join(line)}'")

			if not self.running:
				break

			# evals
			if self.registers["X"].value == SamValue("00000001").value:
				if self.syscall_old == "print":
					print(self.to_string(), sep="", end="")
				elif self.syscall_old == "println":
					print(self.to_string(), sep="")
				elif self.syscall_old == "exit":
					self.running = False
				elif self.syscall_old == "":
					pass
				else:
					error(
						f"Fatal Error | pce {self.pce} | Invalid syscall '{self.syscall_old}'")
				self.syscall_old = ""
			elif self.registers["X"].value == SamValue("00000010").value:
				self.syscall_old = "print"
			elif self.registers["X"].value == SamValue("00000100").value:
				self.syscall_old = "println"
			elif self.registers["X"].value == SamValue("00000011").value:
				self.syscall_old = "exit"
			else:
				self.syscall_old = ""

			if self.registers["ZZ"].value != SamValue("00000000").value:
				if self.registers["ZZ"].value == SamValue("01100000").value:
					self.zz_stack.clear()
				else:
					self.zz_stack.append(self.registers["ZZ"])
					self.registers["ZZ"] = SamValue("00000000")
		self.running = False

	def to_string(self) -> str:
		new_string = ""
		for value in self.zz_stack:
			if value.type != "char":
				value.value = int(value.value, 2)
			new_string += char_list[int(value.value)]
		return new_string

	def compare(self, op: str) -> None:
		self.registers["C"] = SamValue("00000000")
		if op == "EQUAL":
			if self.registers["A"].value == self.registers["B"].value:
				self.registers["C"] = SamValue("00000001")
		elif op == "NOT_EQUAL":
			if self.registers["A"].value != self.registers["B"].value:
				self.registers["C"] = SamValue("00000001")

	def dump(self) -> dict:
		return {
			"registers": {reg: str(self.registers[reg]) for reg in self.registers},
			"memory": {num: str(self.memory[num]) for num in self.memory}
		}

	def table_dump(self) -> None:
		registers = self.dump()["registers"]
		print(*[f"{reg:>3} {value}" for reg, value in registers.items()], sep=" | ")
		print("-" * 97)
		for i in range(0, 64, 5):
			row = [f"{i:>3} " + str(value) for i, value in list(self.dump()["memory"].items())[i:i+5]]
			print(' | '.join(row))
