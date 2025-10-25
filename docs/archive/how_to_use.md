  🚀 How to Use the Workflow Driver

  # From /home/ajs7/project/reflow/

  # Show current step and required actions
  python3 workflow_driver.py dnd_reflow

  # Refresh context (when needed)
  python3 workflow_driver.py dnd_reflow --refresh

  # Mark actions complete as you verify them
  python3 workflow_driver.py dnd_reflow --mark-done D2.1
  python3 workflow_driver.py dnd_reflow --mark-done D2.2

  # Run validation gate (will block if failing)
  python3 workflow_driver.py dnd_reflow --validate

  # Advance to next step (only after validation passes)
  python3 workflow_driver.py dnd_reflow --next

  # Show overall status
  python3 workflow_driver.py dnd_reflow --status

  # Auto detect progress
  python3 workflow_driver.py <system> --auto-detect-progress    # 
  
  # Auto-detect completed actions
  python3 workflow_driver.py <system> --quality-gates           # Run 
  
  # quality gates validation
  python3 workflow_driver.py <system> --auto-detect-progress --dry-run  # 
  Preview detection

