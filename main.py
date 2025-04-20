from sam import SamExt

if __name__ == "__main__":
	st = SamExt()
	with open("test.sam", "r") as f:
		st.connect(f)

	st.run(verbose=True)
