#!/usr/bin/env python3
"""
Content Loop - Knowledge Amendment Engine
Reads analysis reports and proposes specific changes to knowledge files based on performance data.
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from analyze import AnalysisEngine
from config import Config

class KnowledgeAmender:
    def __init__(self, knowledge_dir="knowledge", data_dir="data", config: Config = None):
        self.config = config or Config()
        self.knowledge_dir = self.config.knowledge_dir if config else knowledge_dir
        self.data_dir = self.config.data_dir if config else data_dir
        self.log_file = self.config.log_file if config else os.path.join(data_dir, "run-log.jsonl")
        self.product = self.config.product
    
    def read_knowledge_file(self, filename: str) -> str:
        """Read current knowledge file content"""
        file_path = os.path.join(self.knowledge_dir, filename)
        if not os.path.exists(file_path):
            return ""
        
        with open(file_path, 'r') as f:
            return f.read()
    
    def write_knowledge_file(self, filename: str, content: str) -> None:
        """Write updated knowledge file content"""
        file_path = os.path.join(self.knowledge_dir, filename)
        os.makedirs(self.knowledge_dir, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def backup_knowledge_file(self, filename: str) -> str:
        """Create backup of knowledge file before amendment"""
        source = os.path.join(self.knowledge_dir, filename)
        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
        backup_path = os.path.join(self.knowledge_dir, backup_name)
        
        if os.path.exists(source):
            with open(source, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
        
        return backup_path
    
    def amend_hooks_knowledge(self, winners: List[str], losers: List[str], hook_performances: Dict) -> Tuple[str, str]:
        """Amend hooks.md based on performance data"""
        current_content = self.read_knowledge_file("hooks.md")
        
        # Parse current performance markers
        lines = current_content.split('\n')
        new_lines = []
        
        # Track which hooks we've processed
        processed_hooks = set()
        changes = []
        
        for line in lines:
            # Look for hook entries with performance markers
            hook_match = re.search(r'- \*\*([^*]+)\*\*.*(?:HIGH PERFORMER|TESTING|DROPPED)', line, re.IGNORECASE)
            if hook_match:
                hook_name = hook_match.group(1).lower().replace(' ', '-')
                processed_hooks.add(hook_name)
                
                # Update performance marker based on current analysis
                if hook_name in [w.lower().replace(' ', '-') for w in winners]:
                    if "DROPPED" in line or "TESTING" in line:
                        new_line = re.sub(r'(DROPPED|TESTING)', 'HIGH PERFORMER', line)
                        changes.append(f"Promoted {hook_name} to HIGH PERFORMER")
                    else:
                        new_line = line  # Already high performer
                elif hook_name in [l.lower().replace(' ', '-') for l in losers]:
                    if "HIGH PERFORMER" in line or "TESTING" in line:
                        new_line = re.sub(r'(HIGH PERFORMER|TESTING)', 'DROPPED', line)
                        changes.append(f"Demoted {hook_name} to DROPPED")
                    else:
                        new_line = line  # Already dropped
                else:
                    # Not in winners or losers, mark as testing if not already categorized
                    if not any(marker in line for marker in ["HIGH PERFORMER", "TESTING", "DROPPED"]):
                        new_line = line + " **(TESTING)**"
                        changes.append(f"Marked {hook_name} as TESTING")
                    else:
                        new_line = line
                
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        
        # Add new winning hooks that weren't in the file
        for winner in winners:
            hook_key = winner.lower().replace(' ', '-')
            if hook_key not in processed_hooks:
                # Find performance data
                perf_data = hook_performances.get(hook_key, {})
                avg_views = perf_data.get('avg_views', 0)
                
                new_hook_entry = f"\n- **{winner}**: High-performing hook category with {avg_views:.0f} avg views **(HIGH PERFORMER)**"
                new_lines.append(new_hook_entry)
                changes.append(f"Added new high performer: {winner}")
        
        new_content = '\n'.join(new_lines)
        
        # Generate change summary
        change_summary = '; '.join(changes) if changes else "No changes needed"
        
        return new_content, change_summary
    
    def amend_ctas_knowledge(self, report_data: Dict) -> Tuple[str, str]:
        """Amend ctas.md based on conversion performance"""
        current_content = self.read_knowledge_file("ctas.md")
        
        # Look for conversion rate patterns in findings/recommendations
        changes = []
        new_content = current_content
        
        # If recommendations suggest CTA testing, update the testing section
        recommendations = report_data.get('recommendations', [])
        cta_recs = [r for r in recommendations if 'CTA' in r or 'cta' in r.lower()]
        
        if cta_recs:
            # Add recommendation to test different CTAs
            if "## Currently Testing" not in current_content:
                new_content += "\n\n## Currently Testing\n\n"
            
            for rec in cta_recs:
                if "different CTAs" in rec:
                    testing_note = f"- Testing CTA variants based on analysis from {datetime.now().strftime('%Y-%m-%d')}: {rec}\n"
                    if testing_note not in new_content:
                        new_content += testing_note
                        changes.append("Added CTA testing recommendation")
        
        # If we have conversion data, update performance notes
        if report_data.get('total_conversions', 0) > 0:
            conversion_rate = report_data.get('overall_conversion_rate', 0)
            performance_note = f"\n## Recent Performance\n\n- Overall conversion rate: {conversion_rate:.3%} (as of {datetime.now().strftime('%Y-%m-%d')})\n"
            
            if "Recent Performance" not in current_content:
                new_content += performance_note
                changes.append(f"Added conversion rate tracking: {conversion_rate:.3%}")
        
        change_summary = '; '.join(changes) if changes else "No changes needed"
        return new_content, change_summary
    
    def amend_images_knowledge(self, report_data: Dict) -> Tuple[str, str]:
        """Amend images.md based on visual performance patterns"""
        current_content = self.read_knowledge_file("images.md")
        changes = []
        
        # Look for view-related patterns in the data
        avg_views = report_data.get('avg_views_per_post', 0)
        total_posts = report_data.get('total_posts', 0)
        
        if total_posts >= 3:  # Need enough data for meaningful insights
            # Add performance tracking section
            performance_section = f"""

## Recent Performance Data

- Average views per post: {avg_views:.0f} (last {report_data.get('period', 'period')})
- Total posts analyzed: {total_posts}
- Last updated: {datetime.now().strftime('%Y-%m-%d')}

"""
            
            if "Recent Performance Data" not in current_content:
                new_content = current_content + performance_section
                changes.append(f"Added performance tracking: {avg_views:.0f} avg views")
            else:
                # Update existing performance section
                updated_content = re.sub(
                    r'## Recent Performance Data.*?(?=\n##|\Z)',
                    performance_section.strip(),
                    current_content,
                    flags=re.DOTALL
                )
                new_content = updated_content
                changes.append("Updated performance metrics")
        else:
            new_content = current_content
        
        change_summary = '; '.join(changes) if changes else "No changes needed"
        return new_content, change_summary
    
    def propose_skill_amendments(self, report_data: Dict) -> List[str]:
        """Propose changes to the content creation skill based on performance patterns"""
        proposals = []
        
        # Check if there are systemic issues that suggest skill improvements
        findings = report_data.get('findings', [])
        recommendations = report_data.get('recommendations', [])
        
        # Low overall performance suggests process issues
        avg_views = report_data.get('avg_views_per_post', 0)
        if avg_views < 1000 and report_data.get('total_posts', 0) >= 5:
            proposals.append("Consider updating image generation prompts for more engaging visuals")
            proposals.append("Review text overlay positioning and sizing for better readability")
        
        # High views but low conversions suggests CTA/landing issues
        high_view_low_conversion = any("high views but low conversion" in f.lower() for f in findings)
        if high_view_low_conversion:
            proposals.append("Update CTA placement and wording in slide generation process")
            proposals.append("Consider A/B testing different CTA strategies in the skill")
        
        # Consistent poor performance across hook types
        hook_performances = report_data.get('hook_performances', {})
        if len(hook_performances) >= 3:
            scores = [perf['performance_score'] for perf in hook_performances.values()]
            if max(scores) < 5:  # All hooks performing poorly
                proposals.append("Fundamental hook strategy may need revision - consider new formats")
                proposals.append("Image style might not be resonating - test different visual approaches")
        
        return proposals
    
    def apply_amendments(self, report_file: Optional[str] = None, dry_run: bool = False) -> Dict:
        """Apply amendments based on latest analysis report"""
        # Load latest analysis report
        if report_file:
            with open(report_file, 'r') as f:
                report_data = json.load(f)
        else:
            # Find latest analysis file
            analysis_files = [f for f in os.listdir(self.data_dir) if f.startswith('analysis_') and f.endswith('.json')]
            if not analysis_files:
                return {"error": "No analysis report found"}
            
            latest_report = sorted(analysis_files)[-1]
            with open(os.path.join(self.data_dir, latest_report), 'r') as f:
                report_data = json.load(f)
        
        amendments = {
            "timestamp": datetime.now().isoformat(),
            "source_report": report_file or latest_report,
            "changes": {},
            "skill_proposals": [],
            "dry_run": dry_run
        }
        
        # Extract winners and losers
        winners = report_data.get('winners', [])
        losers = report_data.get('losers', [])
        hook_performances = report_data.get('hook_performances', {})
        
        # Amend hooks knowledge
        if winners or losers:
            if not dry_run:
                self.backup_knowledge_file("hooks.md")
            
            new_hooks_content, hooks_changes = self.amend_hooks_knowledge(winners, losers, hook_performances)
            
            if not dry_run and hooks_changes != "No changes needed":
                self.write_knowledge_file("hooks.md", new_hooks_content)
            
            amendments["changes"]["hooks.md"] = hooks_changes
        
        # Amend CTAs knowledge
        if not dry_run:
            self.backup_knowledge_file("ctas.md")
        
        new_ctas_content, ctas_changes = self.amend_ctas_knowledge(report_data)
        
        if not dry_run and ctas_changes != "No changes needed":
            self.write_knowledge_file("ctas.md", new_ctas_content)
        
        amendments["changes"]["ctas.md"] = ctas_changes
        
        # Amend images knowledge
        if not dry_run:
            self.backup_knowledge_file("images.md")
        
        new_images_content, images_changes = self.amend_images_knowledge(report_data)
        
        if not dry_run and images_changes != "No changes needed":
            self.write_knowledge_file("images.md", new_images_content)
        
        amendments["changes"]["images.md"] = images_changes
        
        # Generate skill proposals
        amendments["skill_proposals"] = self.propose_skill_amendments(report_data)
        
        # Log the amendment
        if not dry_run:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "amendment",
                "changes": amendments["changes"],
                "skill_proposals": amendments["skill_proposals"],
                "source": amendments["source_report"]
            }
            
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        return amendments

def main():
    """CLI for applying knowledge amendments"""
    cfg = Config()
    amender = KnowledgeAmender(config=cfg)
    print(f"[product: {cfg.product} | knowledge: {amender.knowledge_dir}]")
    
    if len(sys.argv) < 2:
        print("Usage: python amend.py <command> [args...]")
        print("Commands:")
        print("  apply [report_file]  # Apply amendments from analysis report")
        print("  dry-run [report_file]  # Show what would be changed without applying")
        print("  backup <file>        # Create backup of knowledge file")
        return
    
    command = sys.argv[1]
    
    if command == "apply":
        report_file = sys.argv[2] if len(sys.argv) > 2 else None
        amendments = amender.apply_amendments(report_file, dry_run=False)
        
        if "error" in amendments:
            print(f"Error: {amendments['error']}")
            return
        
        print(f"\n=== KNOWLEDGE AMENDMENTS APPLIED ===")
        print(f"Source report: {amendments['source_report']}")
        print(f"Timestamp: {amendments['timestamp']}")
        
        for file, changes in amendments['changes'].items():
            print(f"\n📝 {file}:")
            print(f"  {changes}")
        
        if amendments['skill_proposals']:
            print(f"\n🔧 SKILL IMPROVEMENT PROPOSALS:")
            for proposal in amendments['skill_proposals']:
                print(f"  • {proposal}")
        
        print(f"\nAmendments logged to run-log.jsonl")
        
    elif command == "dry-run":
        report_file = sys.argv[2] if len(sys.argv) > 2 else None
        amendments = amender.apply_amendments(report_file, dry_run=True)
        
        if "error" in amendments:
            print(f"Error: {amendments['error']}")
            return
        
        print(f"\n=== DRY RUN - PROPOSED CHANGES ===")
        print(f"Source report: {amendments['source_report']}")
        
        for file, changes in amendments['changes'].items():
            if changes != "No changes needed":
                print(f"\n📝 Would change {file}:")
                print(f"  {changes}")
            else:
                print(f"\n📝 {file}: No changes needed")
        
        if amendments['skill_proposals']:
            print(f"\n🔧 SKILL IMPROVEMENT PROPOSALS:")
            for proposal in amendments['skill_proposals']:
                print(f"  • {proposal}")
        else:
            print(f"\n🔧 No skill improvements suggested")
        
        print(f"\n(No files modified - this was a dry run)")
        
    elif command == "backup":
        if len(sys.argv) < 3:
            print("Usage: python amend.py backup <filename>")
            return
            
        filename = sys.argv[2]
        backup_path = amender.backup_knowledge_file(filename)
        print(f"Backup created: {backup_path}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()