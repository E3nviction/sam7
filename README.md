# SAM7 Emulator

Welcome to the **SAM7 Emulator**! This project was a fun school project designed to emulate a simple esoteric assembly-like language with basic memory and register operations. The emulator is written in Python and provides a way to execute `.sam` files with custom instructions.

---

## Features

- **Custom Assembly Language**: Supports basic instructions like `LDI`, `LTM`, `BRK`, `BN`, `CMP`, and more.
- **Registers and Memory**: Simulates registers (`A`, `B`, `C`, `X`, `E`, `ZZ`) and a memory space of 64 addresses.
- **Syscalls**: Includes basic syscalls for printing, exiting, and stack manipulation.
- **Label Support**: Allows branching and conditional execution using labels.
- **Error Handling**: Provides detailed error messages for invalid instructions or values.

---

## How to Run

- Clone the repository:

```bash
git clone https://github.com/e3nviction/sam7
cd sam7
```

- Run the emulator with the provided sample file:

```bash
python3 main.py
```

- Modify `test.sam` to write your own instructions and experiment with the emulator.

---

## Sample `.sam` File

Here’s an example of a `.sam` file (`test.sam`):

```go
// Load values into registers
LDI A 100
LDI B 011

// Print "Hello"
LDI ZZ "H"
LDI ZZ "e"
LDI ZZ "l"
LDI ZZ "l"
LDI ZZ "o"
LDI ZZ 0
LDI X 100
LDI X 1
```

---

## How It Works

It uses the "use and push" method, which basically means that everything is read from the top of the stack and then removed.

---

## Example Output

Running the provided `test.sam` file will output:

```bash
Hello

Exiting...
```

---

## License

This project was created as a school project and is shared for educational purposes. Feel free to experiment and modify it!

---

Enjoy exploring the SAM7 Emulator! 🎉
