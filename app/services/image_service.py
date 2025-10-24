import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings


class ImageService:
    """Service for generating summary images"""

    def __init__(self):
        self.cache_dir = Path(settings.CACHE_DIR)
        self.image_path = self.cache_dir / "summary.png"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def generate_summary_image(
        self,
        total_countries: int,
        top_countries: List[Tuple[str, float]],
        last_refreshed: datetime,
    ) -> str:
        """
        Generate a summary image with country statistics

        Args:
            total_countries: Total number of countries
            top_countries: List of (country_name, gdp) tuples for top 5 countries
            last_refreshed: Timestamp of last refresh

        Returns:
            Path to the generated image
        """
        # Image dimensions
        width = 800
        height = 600
        background_color = (255, 255, 255)
        text_color = (0, 0, 0)
        header_color = (41, 128, 185)
        line_color = (200, 200, 200)

        # Create image
        image = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(image)

        # Try to use a better font, fallback to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
            header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except (IOError, OSError):
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        y_position = 30

        # Title
        title = "Country Currency Summary"
        draw.text(
            (width // 2, y_position),
            title,
            fill=header_color,
            font=title_font,
            anchor="mt",
        )
        y_position += 60

        # Horizontal line
        draw.line(
            [(50, y_position), (width - 50, y_position)], fill=line_color, width=2
        )
        y_position += 30

        # Total countries
        total_text = f"Total Countries: {total_countries}"
        draw.text(
            (width // 2, y_position),
            total_text,
            fill=text_color,
            font=header_font,
            anchor="mt",
        )
        y_position += 50

        # Top 5 countries header
        if top_countries:
            top_header = "Top 5 Countries by Estimated GDP"
            draw.text(
                (width // 2, y_position),
                top_header,
                fill=header_color,
                font=header_font,
                anchor="mt",
            )
            y_position += 40

            # List top countries
            for idx, (country_name, gdp) in enumerate(top_countries, 1):
                if gdp is not None:
                    gdp_formatted = f"${gdp:,.2f}"
                else:
                    gdp_formatted = "N/A"

                country_text = f"{idx}. {country_name}: {gdp_formatted}"
                draw.text(
                    (100, y_position), country_text, fill=text_color, font=body_font
                )
                y_position += 35

        # Horizontal line
        y_position += 20
        draw.line(
            [(50, y_position), (width - 50, y_position)], fill=line_color, width=2
        )
        y_position += 30

        # Last refreshed timestamp
        timestamp_text = (
            f"Last Refreshed: {last_refreshed.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        draw.text(
            (width // 2, y_position),
            timestamp_text,
            fill=text_color,
            font=small_font,
            anchor="mt",
        )

        # Save image
        image.save(self.image_path)
        return str(self.image_path)

    def image_exists(self) -> bool:
        """Check if summary image exists"""
        return self.image_path.exists()

    def get_image_path(self) -> str:
        """Get the path to the summary image"""
        return str(self.image_path)

    def delete_image(self) -> None:
        """Delete the summary image if it exists"""
        if self.image_path.exists():
            os.remove(self.image_path)


# Create a singleton instance
image_service = ImageService()
