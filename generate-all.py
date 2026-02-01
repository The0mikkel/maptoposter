#!/usr/bin/env python3.13
# This file can be run directly to generate map posters for all available themes.

import os
import argparse
import subprocess

# Get all files from themes directory
THEMES_DIR = os.path.join(os.path.dirname(__file__), 'themes')
THEME_FILES = [f for f in os.listdir(THEMES_DIR) if f.endswith('.json')]

AVAILABLE_THEMES = [os.path.splitext(f)[0] for f in THEME_FILES]
def list_available_themes():
    return AVAILABLE_THEMES

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wrapper for generating map posters for all themes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python3.13 generate-all.py --city "Tokyo" --country "Japan" --distance 20000 --width 15 --height 20 --output "./posters"
This will generate map posters for Tokyo, Japan with a distance of 20000 meters, width of 15 inches, height of 20 inches, 
and save them in the ./posters directory with subdirectory following the format of `{country}/{city}/{distance}/{size}`.

It is possible to specify an additional subdirectory within the size directory using the --output-subdir option.
  python3.13 generate-all.py --city "Tokyo" --country "Japan" --distance 20000 --width 15 --height 20 --output "./posters" --output-subdir "v1"
This will save the posters in `./posters/Japan/Tokyo/20km/15in_x_20in/v1/`.
        """
    )
    parser.add_argument('--output', '-o', type=str, default=None, help='Output directory (optional)')
    parser.add_argument('--output-subdir', '-os', type=str, default=None, help='Output subdirectory (optional)')
    
    parser.add_argument("--city", "-c", type=str, help="City name")
    parser.add_argument("--country", "-C", type=str, help="Country name")
    parser.add_argument(
        "--latitude",
        "-lat",
        dest="latitude",
        type=str,
        help="Override latitude center point",
    )
    parser.add_argument(
        "--longitude",
        "-long",
        dest="longitude",
        type=str,
        help="Override longitude center point",
    )
    parser.add_argument(
        "--country-label",
        dest="country_label",
        type=str,
        help="Override country text displayed on poster",
    )
    parser.add_argument(
        "--theme",
        "-t",
        type=str,
        default="terracotta",
        help="Theme name (default: terracotta)",
    )
    parser.add_argument(
        "--all-themes",
        "--All-themes",
        dest="all_themes",
        action="store_true",
        help="Generate posters for all themes",
    )
    parser.add_argument(
        "--distance",
        "-d",
        type=int,
        default=18000,
        help="Map radius in meters (default: 18000)",
    )
    parser.add_argument(
        "--width",
        "-W",
        type=float,
        default=12,
        help="Image width in inches (default: 12, max: 20 )",
    )
    parser.add_argument(
        "--height",
        "-H",
        type=float,
        default=16,
        help="Image height in inches (default: 16, max: 20)",
    )
    parser.add_argument(
        "--list-themes", action="store_true", help="List all available themes"
    )
    parser.add_argument(
        "--display-city",
        "-dc",
        type=str,
        help="Custom display name for city (for i18n support)",
    )
    parser.add_argument(
        "--display-country",
        "-dC",
        type=str,
        help="Custom display name for country (for i18n support)",
    )
    parser.add_argument(
        "--font-family",
        type=str,
        help='Google Fonts family name (e.g., "Noto Sans JP", "Open Sans"). If not specified, uses local Roboto fonts.',
    )
    parser.add_argument(
        "--format",
        "-f",
        default="png",
        choices=["png", "svg", "pdf"],
        help="Output format for the poster (default: png)",
    )
    parser.add_argument(
        "--no-water",
        action="store_true",
        help="Do not render water features on the map",
    )

    args = parser.parse_args()
    
    themes = list_available_themes()
    
    # Create output directory if specified
    if args.output and not os.path.exists(args.output):
        os.makedirs(args.output)
    
    print(f"Generating posters for {args.city}, {args.country} with distance {args.distance}m...\n")
    
    # Convert distance to text for directory
    if args.distance >= 1000:
        distance_text = f"{args.distance // 1000}km"
    else:
        distance_text = f"{args.distance}m"
        
    # convert width and height to text for directory
    width_text = f"{int(args.width)}in"
    height_text = f"{int(args.height)}in"
    size_text = f"{width_text}_x_{height_text}"
    
    # Run create_map_poster.py to generate posters with the listed themes.
    for theme in themes:
        print(f"Generating poster with theme: {theme}...")
        cmd = f'python3.13 create_map_poster.py --city "{args.city}" --country "{args.country}" --theme {theme} --distance {args.distance} --width {args.width} --height {args.height} --format {args.format}'
        if args.latitude:
            cmd += f' --latitude {args.latitude}'
        if args.longitude:
            cmd += f' --longitude {args.longitude}'
        if args.country_label:
            cmd += f' --country-label "{args.country_label}"'
        if args.display_city:
            cmd += f' --display-city "{args.display_city}"'
        if args.display_country:
            cmd += f' --display-country "{args.display_country}"'
        if args.font_family:
            cmd += f' --font-family "{args.font_family}"'
        if args.no_water:
            cmd += ' --no-water'
        if args.output:
            output_file = f"{args.output}/{args.country}/{args.city}/{distance_text}/{size_text}"
            if args.output_subdir:
                output_file = f"{output_file}/{args.output_subdir}"
            cmd += f' --output "{output_file}"'
        subprocess.run(cmd, shell=True)
        print(f"Poster with theme {theme} generated.\n")
        
    print("\nAll posters generated successfully!")


