import sys

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["mouse", "camera", "camera_black"]:
        print("Usage: python dreamy.py [mouse | camera | camera_black]")
        sys.exit(1)

    if sys.argv[1] == "mouse":
        from src.mouse import main

        main()
    elif sys.argv[1] == "camera":
        from src.hand import main

        main()
    elif sys.argv[1] == "camera_black":
        from src.hand_black import main

        main()
