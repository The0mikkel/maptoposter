#!/usr/bin/env python3.13
# This file can be run directly to generate map posters for all available themes.

import os
import argparse
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        choices=["png", "svg", "pdf", "png+svg", "png+pdf", "svg+pdf", "png+svg+pdf"],
        help="Output format for the poster (default: png)",
    )
    parser.add_argument(
        "--no-water",
        action="store_true",
        help="Do not render water features on the map",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of parallel threads for generating posters (default: 4)",
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
    
    # Track successful and failed themes with timing
    successful_themes = []
    failed_themes = []
    theme_times = {}
    
    # Record overall start time
    overall_start_time = time.time()
    
    # Function to run a single theme generation
    def generate_theme(theme):
        try:
            theme_start_time = time.time()
            print(f"Generating poster with theme: {theme}...")
            cmd = f'python3.13 create_map_poster.py --city "{args.city}" --country "{args.country}" --theme {theme} --distance {args.distance} --width {args.width} --height {args.height} --format {args.format}'
            cmd += f' --dpi {args.dpi}'
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
            
            result = subprocess.run(cmd, shell=True, capture_output=False)
            
            theme_elapsed_time = time.time() - theme_start_time
            theme_times[theme] = theme_elapsed_time
            
            if result.returncode == 0:
                print(f"Poster with theme {theme} generated. ({theme_elapsed_time:.1f}s)\n")
                return (theme, True, None, theme_elapsed_time)
            else:
                error_msg = f"Process exited with code {result.returncode}"
                print(f"Failed to generate poster with theme {theme}: {error_msg} ({theme_elapsed_time:.1f}s)\n")
                return (theme, False, error_msg, theme_elapsed_time)
        except Exception as exc:
            theme_elapsed_time = time.time() - theme_start_time
            theme_times[theme] = theme_elapsed_time
            error_msg = str(exc)
            print(f"Failed to generate poster with theme {theme}: {error_msg} ({theme_elapsed_time:.1f}s)\n")
            return (theme, False, error_msg, theme_elapsed_time)
    
    # Run create_map_poster.py to generate posters with the listed themes.
    # First theme runs sequentially, rest run in parallel
    if themes:
        # Run first theme
        first_theme = themes[0]
        theme, success, error, elapsed = generate_theme(first_theme)
        if success:
            successful_themes.append(theme)
        else:
            failed_themes.append((theme, error))
        
        # Run remaining themes in parallel
        if len(themes) > 1:
            remaining_themes = themes[1:]
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = [executor.submit(generate_theme, theme) for theme in remaining_themes]
                for future in as_completed(futures):
                    try:
                        theme, success, error, elapsed = future.result()
                        if success:
                            successful_themes.append(theme)
                        else:
                            failed_themes.append((theme, error))
                    except Exception as exc:
                        print(f"Theme generation raised an exception: {exc}")
                        failed_themes.append(("unknown", str(exc)))
    
    # Calculate total time
    total_elapsed_time = time.time() - overall_start_time
    
    # Print summary
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    print(f"Total themes: {len(themes)}")
    print(f"Successful: {len(successful_themes)}")
    print(f"Failed: {len(failed_themes)}")
    
    if successful_themes:
        print(f"\n✓ Successfully generated themes:")
        for theme in successful_themes:
            theme_time = theme_times.get(theme, 0)
            print(f"  - {theme} ({theme_time:.1f}s)")
    
    if failed_themes:
        print(f"\n✗ Failed themes:")
        for theme, error in failed_themes:
            theme_time = theme_times.get(theme, 0)
            print(f"  - {theme}: {error} ({theme_time:.1f}s)")
        print("\nSome posters failed to generate. Check the errors above.")
    else:
        print("\nAll posters generated successfully!")
    
    # Print timing summary
    print(f"\n" + "="*60)
    print(f"Total execution time: {total_elapsed_time:.1f}s ({total_elapsed_time/60:.1f}m)")
    if theme_times:
        avg_time = sum(theme_times.values()) / len(theme_times)
        print(f"Average time per theme: {avg_time:.1f}s")
    print("="*60)


