from missions import all_missions
from simulator import run_mission


def main() -> None:
    missions = all_missions()
    completed = set()

    while True:
        print("\nOSI COMMUNICATION SIMULATOR")
        print("SELECT A MISSION")
        for mission in missions:
            status = "✓" if mission.mission_id in completed else " "
            print(f"[{status}] {mission.mission_id}. {mission.icon} {mission.name} - {mission.description}")
        print("0. Exit")

        choice = input("\nMission number: ").strip()
        if choice == "0":
            break
        if not choice.isdigit():
            print("Invalid choice.")
            continue

        selected = next((m for m in missions if m.mission_id == int(choice)), None)
        if not selected:
            print("Mission not found.")
            continue

        run_mission(selected)
        completed.add(selected.mission_id)

    print("Goodbye.")


if __name__ == "__main__":
    main()
