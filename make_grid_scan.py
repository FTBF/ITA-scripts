#!/usr/bin/env python3
import argparse
import json
from typing import List, Dict


ORDINAL_WORDS = {
    1: "First",
    2: "Second",
    3: "Third",
    4: "Fourth",
    5: "Fifth",
    6: "Sixth",
    7: "Seventh",
    8: "Eighth",
    9: "Ninth",
    10: "Tenth",
    11: "Eleventh",
    12: "Twelfth",
    13: "Thirteenth",
    14: "Fourteenth",
    15: "Fifteenth",
}


def ordinal_word(n: int) -> str:
    """Return an English ordinal word for small integers."""
    return ORDINAL_WORDS.get(n, f"{n}th")


def parse_list_file(path: str) -> List[int]:
    """Read a text file with one numeric value per line."""
    values: List[int] = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            values.append(int(line))
    return values


def build_h_dose_pattern(
    hsteps_sorted: List[int],
    low_dose: int,
    med_dose: int,
    high_dose: int,
) -> List[int]:
    """
    Assign doses to the horizontal positions:
      - min (index 0) and max (index n-1): low dose
      - interior positions:
          * first half: medium dose
          * second half: high dose
        with the understanding that "except the first/last" is handled by
        keeping indices 0 and n-1 as low-dose.
    """
    n = len(hsteps_sorted)
    if n == 0:
        raise ValueError("Need at least one HSTEP position")
    if n == 1:
        # Only one H step, everything is low dose by definition
        return [low_dose]

    doses = [low_dose] * n  # default all low

    if n <= 2:
        # Only min and max exist → both low, nothing else to split
        return doses

    # interior indices: 1 .. n-2
    interior_indices = list(range(1, n - 1))
    k = len(interior_indices)
    # Split interior roughly in half
    # first half -> medium, second half -> high
    mid = k // 2  # number of elements that will get medium

    for idx in interior_indices[:mid]:
        doses[idx] = med_dose
    for idx in interior_indices[mid:]:
        doses[idx] = high_dose

    return doses

def generate_serpentine_grid(
    hsteps: List[int],
    vsteps: List[int],
    low_dose: int,
    med_dose: int,
    high_dose: int,
) -> List[Dict]:
    """
    Generate a serpentine scan pattern as a flat list of dictionaries.

    Pattern:
      - Initial positioning at min H and min V (both low dose).
      - For each VSTEP (row), do a horizontal scan:
          * odd-numbered rows (1-based): H from low → high
          * even-numbered rows: H from high → low
        BUT:
          * Do NOT re-visit the starting H position for that row
            (the motor is already there).
      - Between rows, insert a vertical step with low dose.
      - Add comments before each horizontal scan and vertical move.
    """

    if not hsteps:
        raise ValueError("No HSTEP positions provided")
    if not vsteps:
        raise ValueError("No VSTEP positions provided")

    # Sort positions
    h_sorted = sorted(hsteps)
    v_sorted = sorted(vsteps)

    # Precompute dose per horizontal index
    h_doses = build_h_dose_pattern(h_sorted, low_dose, med_dose, high_dose)

    steps: List[Dict] = []
    hstep_index = 1
    vstep_index = 1

    # Initial positioning: move to min H, then to min V
    steps.append({"comment": "Initial Positioning"})
    steps.append(
        {
            "stepname": f"HSTEP{hstep_index}",
            "pos": h_sorted[0],
            "dose": low_dose,
        }
    )
    hstep_index += 1

    steps.append(
        {
            "stepname": f"VSTEP{vstep_index}",
            "pos": v_sorted[0],
            "dose": low_dose,
        }
    )
    vstep_index += 1

    # Track where the motor is horizontally (index into h_sorted)
    current_h_idx = 0

    # Horizontal scans at each V position
    for row_idx, v_pos in enumerate(v_sorted, start=1):
        # Comment for this horizontal line scan
        steps.append(
            {"comment": f"{ordinal_word(row_idx)} Horizontal Line Scan"}
        )

        n_h = len(h_sorted)

        # Determine H scan order for this row (serpentine)
        if (row_idx % 2) == 1:
            # odd row: left to right (low → high)
            h_range = range(n_h)
        else:
            # even row: right to left (high → low)
            h_range = range(n_h - 1, -1, -1)

        # Move along this row, but skip the first index if it's
        # exactly where we already are (no need to step there again).
        for idx in h_range:
            if idx == current_h_idx:
                continue  # already at this H position
            steps.append(
                {
                    "stepname": f"HSTEP{hstep_index}",
                    "pos": h_sorted[idx],
                    "dose": h_doses[idx],
                }
            )
            hstep_index += 1
            current_h_idx = idx  # update motor location

        # After this horizontal pass, if there is another V row, step vertically
        if row_idx < len(v_sorted):
            steps.append(
                {"comment": f"{ordinal_word(row_idx)} Vertical Step"}
            )
            steps.append(
                {
                    "stepname": f"VSTEP{vstep_index}",
                    "pos": v_sorted[row_idx],  # next V position
                    "dose": low_dose,
                }
            )
            vstep_index += 1
            # Note: current_h_idx stays at the end of the row,
            # so the next row starts from that H position
            # and will skip it on the first HSTEP.
    return steps


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a serpentine grid-scan JSON file from HSTEP and VSTEP positions."
        )
    )

    # Output
    parser.add_argument(
        "-o",
        "--output",
        default="grid_scan.json",
        help="Output JSON filename (default: grid_scan.json)",
    )

    # HSTEP sources
    parser.add_argument(
        "--hsteps",
        type=int,
        nargs="+",
        help="List of horizontal positions (HSTEPs) as ints.",
    )
    parser.add_argument(
        "--hfile",
        help="Text file with one horizontal position per line.",
    )

    # VSTEP sources
    parser.add_argument(
        "--vsteps",
        type=int,
        nargs="+",
        help="List of vertical positions (VSTEPs) as ints.",
    )
    parser.add_argument(
        "--vfile",
        help="Text file with one vertical position per line.",
    )

    # Doses
    parser.add_argument(
        "--dose-low",
        type=int,
        default=1.00e13,
        help="Low dose (for VSTEPs and min/max HSTEPs). Default: 1.00e13",
    )
    parser.add_argument(
        "--dose-med",
        type=int,
        default=6.02e13,
        help="Medium dose (first half of interior HSTEPs). Default: 6.02e13",
    )
    parser.add_argument(
        "--dose-high",
        type=int,
        default=1.20e14,
        help="High dose (second half of interior HSTEPs). Default: 1.20e14",
    )

    return parser


def get_positions(
    args: argparse.Namespace,
    list_attr: str,
    file_attr: str,
    kind: str,
) -> List[int]:
    """Resolve positions from either a list on the command line or a file."""
    list_values = getattr(args, list_attr)
    file_path = getattr(args, file_attr)

    if list_values and file_path:
        raise ValueError(
            f"Specify either --{list_attr} or --{file_attr}, not both, for {kind} positions."
        )
    if list_values:
        return list_values
    if file_path:
        return parse_list_file(file_path)

    raise ValueError(
        f"No {kind} positions provided. Use --{list_attr} or --{file_attr}."
    )


def main() -> None:
    parser = build_argparser()
    args = parser.parse_args()

    try:
        hsteps = get_positions(args, "hsteps", "hfile", "HSTEP")
        vsteps = get_positions(args, "vsteps", "vfile", "VSTEP")
    except ValueError as e:
        parser.error(str(e))

    steps = generate_serpentine_grid(
        hsteps=hsteps,
        vsteps=vsteps,
        low_dose=int(args.dose_low),
        med_dose=int(args.dose_med),
        high_dose=int(args.dose_high),
    )

    with open(args.output, "w") as f:
        json.dump(steps, f, indent=2)

    print(f"Wrote {len(steps)} steps to {args.output}")


if __name__ == "__main__":
    main()
