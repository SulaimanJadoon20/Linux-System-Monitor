import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import datetime

console = Console()


class SystemMonitor:
    #Monitor system information using subprocess and display with Rich
    
    def __init__(self):
        self.logged_in_users = []
        self.current_user = ""
        self.processes = []
        self.services = []
        self.network_connections = []
        
    def get_logged_in_users(self):
        #Get currently logged-in users using who and whoami
        try:
            console.print("[yellow]Fetching logged-in users...[/yellow]")
            
            # Get current user
            try:
                whoami_result = subprocess.run(
                    ['whoami'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                self.current_user = whoami_result.stdout.strip()
            except Exception as e:
                console.print(f"[red]Error getting current user: {e}[/red]")
                self.current_user = "Unknown"
            
            # Get all logged-in users
            try:
                who_result = subprocess.run(
                    ['who'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if who_result.stdout:
                    lines = who_result.stdout.strip().split('\n')
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 3:
                            self.logged_in_users.append({
                                'user': parts[0],
                                'tty': parts[1],
                                'login_time': ' '.join(parts[2:4]),
                                'from': parts[4] if len(parts) > 4 else "Local"
                            })
            except Exception as e:
                console.print(f"[red]Error getting who output: {e}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error in get_logged_in_users: {e}[/red]")
    
    def get_processes(self):
        #Get ALL running processes using ps
        try:
            console.print("[yellow]Fetching ALL processes...[/yellow]")
            
            ps_result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            lines = ps_result.stdout.strip().split('\n')
            
            
            process_list = []
            for line in lines[1:]:
                parts = line.split(maxsplit=10)  
                if len(parts) >= 11:
                    process_list.append({
                        'user': parts[0],
                        'pid': parts[1],
                        'cpu': parts[2],
                        'mem': parts[3],
                        'vsz': parts[4],
                        'rss': parts[5],
                        'command': parts[10]  
                    })
            
            self.processes = sorted(
                process_list,
                key=lambda x: float(x['cpu']),
                reverse=True
            )  
            
            console.print(f"[green]Found {len(self.processes)} processes[/green]")
            
        except Exception as e:
            console.print(f"[red]Error in get_processes: {e}[/red]")
    
    def get_services(self):
        #Get ALL services status using systemctl
        try:
            console.print("[yellow]Fetching ALL services...[/yellow]")
            
            # Get total services
            try:
                total_result = subprocess.run(
                    ['systemctl', 'list-units', '--type=service', '-q'],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                total_services = len(total_result.stdout.strip().split('\n'))
            except Exception as e:
                console.print(f"[red]Error getting total services: {e}[/red]")
                total_services = 0
            
            # Get enabled services
            try:
                enabled_result = subprocess.run(
                    ['systemctl', 'list-unit-files', '--type=service'],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                lines = enabled_result.stdout.strip().split('\n')
                
                for line in lines[:-1]:  # Skip last summary line
                    parts = line.split()
                    if len(parts) >= 2:
                        service_name = parts[0]  
                        status = parts[1]
                        
                        try:
                            active_result = subprocess.run(
                                ['systemctl', 'is-active', service_name],
                                capture_output=True,
                                text=True,
                                timeout=3
                            )
                            active_status = active_result.stdout.strip()
                        except:
                            active_status = "unknown"
                        
                        self.services.append({
                            'service': service_name, 
                            'enabled': status,
                            'active': active_status
                        })
            
                console.print(f"[green]Found {len(self.services)} services[/green]")
                
            except Exception as e:
                console.print(f"[red]Error getting enabled services: {e}[/red]")
                
        except Exception as e:
            console.print(f"[red]Error in get_services: {e}[/red]")
    
    def get_network_connections(self):
        #Get network connections using ss command
        try:
            console.print("[yellow]Fetching network connections...[/yellow]")
            
            ss_result = subprocess.run(
                ['ss', '-tlnp'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = ss_result.stdout.strip().split('\n')
            
            for line in lines[1:]: 
                parts = line.split()
                if len(parts) >= 4:
                    self.network_connections.append({
                        'state': parts[0],
                        'local': parts[3],
                        'remote': parts[4] if len(parts) > 4 else "N/A",
                        'process': parts[6] if len(parts) > 6 else "kernel"
                    })
            
            # Get top 20 connections (network can be many)
            self.network_connections = self.network_connections[:20]
            console.print(f"[green]Found {len(self.network_connections)} network connections[/green]")
            
        except FileNotFoundError:
            console.print("[red]ss command not found, trying netstat...[/red]")
            try:
                netstat_result = subprocess.run(
                    ['netstat', '-tlnp'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                lines = netstat_result.stdout.strip().split('\n')
                
                for line in lines[2:]: 
                    parts = line.split()
                    if len(parts) >= 4:
                        self.network_connections.append({
                            'state': parts[0],
                            'local': parts[3],
                            'remote': parts[4] if len(parts) > 4 else "N/A",
                            'process': parts[6] if len(parts) > 6 else "kernel"
                        })
                
                self.network_connections = self.network_connections[:20]
                
            except Exception as e:
                console.print(f"[red]Error getting network connections: {e}[/red]")
        
        except Exception as e:
            console.print(f"[red]Error in get_network_connections: {e}[/red]")
    
    def create_logged_in_panel(self):
        #Create top panel showing logged-in users
        panel_table = Table(
            title="Currently Logged-In Users",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            title_style="bold white"
        )
        
        panel_table.add_column("Current User", style="green", width=25)
        panel_table.add_column("TTY", style="blue", width=15)
        panel_table.add_column("Login Time", style="yellow", width=25)
        panel_table.add_column("From/Host", style="magenta", width=40)
        
        if not self.logged_in_users:
            panel_table.add_row("[red]No users logged in[/red]", "", "", "")
        
        for user in self.logged_in_users:
            panel_table.add_row(
                user['user'],
                user['tty'],
                user['login_time'],
                user['from']
            )
        
        return Panel(
            panel_table,
            title="[bold cyan]SYSTEM LOGIN STATUS[/bold cyan]",
            border_style="blue",
            padding=(1, 2)
        )
    
    def create_processes_table(self):
        
        table = Table(
            title=f"All Running Processes ({len(self.processes)} total)",
            show_header=True,
            header_style="bold green",
            box=box.ROUNDED,
            title_style="bold white"
        )
        
        table.add_column("User", style="cyan", width=15)
        table.add_column("PID", style="yellow", width=8)
        table.add_column("CPU%", style="red", width=8)
        table.add_column("MEM%", style="magenta", width=8)
        table.add_column("VSZ", style="blue", width=10)
        table.add_column("RSS", style="blue", width=10)
        table.add_column("Command", style="green") 
        
        if not self.processes:
            table.add_row("[red]No processes found[/red]", "", "", "", "", "", "")
        
        for proc in self.processes:
            table.add_row(
                proc['user'],
                proc['pid'],
                proc['cpu'],
                proc['mem'],
                proc['vsz'],
                proc['rss'],
                proc['command']
            )
        
        return table
    
    def create_services_table(self):
        """Create services table with ALL services"""
        table = Table(
            title=f"All System Services ({len(self.services)} total)",
            show_header=True,
            header_style="bold yellow",
            box=box.ROUNDED,
            title_style="bold white"
        )
        
        table.add_column("Service Name", style="cyan") 
        table.add_column("Enabled", style="blue", width=15)
        table.add_column("Active", style="green", width=15)
        
        if not self.services:
            table.add_row("[red]No services found[/red]", "", "")
        
        for service in self.services:
            
            active_color = "green" if service['active'] == 'active' else "red"
            
            table.add_row(
                service['service'], 
                "[bold blue]" + service['enabled'] + "[/bold blue]",
                f"[{active_color}]{service['active']}[/{active_color}]"
            )
        
        return table
    
    def create_network_table(self):
        #Create network connections table
        table = Table(
            title=f"Network Connections ({len(self.network_connections)} Listening Ports)",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            title_style="bold white"
        )
        
        table.add_column("State", style="cyan", width=10)
        table.add_column("Local Address:Port", style="blue", width=25)
        table.add_column("Remote Address", style="yellow", width=25)
        table.add_column("Process", style="green", width=30)
        
        if not self.network_connections:
            table.add_row("[red]No connections found[/red]", "", "", "")
        
        for conn in self.network_connections:
            table.add_row(
                conn['state'],
                conn['local'],
                conn['remote'],
                conn['process']
            )
        
        return table
    
    def display(self):
        """Display all information in Rich format"""
        console.clear()
        
        # Print title
        console.print(
            Panel(
                "[bold cyan]LINUX SYSTEM MONITOR - FULL VERSION[/bold cyan]\n" +
                f"[yellow]Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/yellow]\n" +
                f"[green]Current User: {self.current_user}[/green]",
                border_style="cyan",
                padding=(1, 2)
            )
        )
        
        console.print()
        
        # Display logged-in users pane
        console.print(self.create_logged_in_panel())
        console.print()
        
        
        console.print(self.create_processes_table())
        console.print()
        
    
        console.print(self.create_services_table())
        console.print()
        
    
        console.print(self.create_network_table())
        console.print()
        
        # Print footer
        console.print(
            Panel(
                "[bold green]System monitoring complete[/bold green]",
                border_style="green",
                padding=(0, 2)
            )
        )


def main():
    #Main function
    try:
        console.print(
            "[bold cyan]Initializing Linux System Monitor...[/bold cyan]\n"
        )
        
        monitor = SystemMonitor()
        
        # Fetch all data
        monitor.get_logged_in_users()
        monitor.get_processes()
        monitor.get_services()
        monitor.get_network_connections()
        
        console.print("\n[bold green]All data fetched successfully![/bold green]\n")
        
        # Display results
        monitor.display()
        
    except KeyboardInterrupt:
        console.print("\n[red]Program interrupted by user[/red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
