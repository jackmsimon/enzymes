import asyncio
from pathlib import Path
import research
import design

async def main():
    # Run research phase
    print("Starting research phase...")
    await research.async_main()
    
    # Verify report was generated
    report_path = Path("/Users/jacksimon/Enzymes/files/report.txt")
    if not report_path.exists():
        raise FileNotFoundError("Research phase failed to generate report.txt")
    
    # Run design phase
    print("\nStarting design phase...")
    design.main()

if __name__ == "__main__":
    asyncio.run(main())