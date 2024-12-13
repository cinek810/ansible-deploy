"""Module for formatting outputs from different sources"""

class Formatters:
    """Class handling formatting of ansible standard output and error streams"""

    error_indicators = ["ERROR", "fatal"]
    task_indicators = ["TASK", "RUNNING HANDLER"]

    def __init__(self, logger):
        self.logger = logger

    def positive_ansible_output(self, warning: list, output: list, command: str):
        """Log output for a positive case in ansible execution"""
        if warning:
            full_warning = "\n\n".join(warning)
            self.logger.warning(f"\n{full_warning}")
        self.logger.info("\"%s\" ran succesfully", " ".join(command))

    def negative_ansible_output(self, warning: list, error: list, command: str):
        """Log output for a negative case in ansible execution"""
        if warning:
            full_warning = "\n\n".join(warning)
            self.logger.warning(f"\n{full_warning}")
        self.logger.error("\"%s\" failed due to:", " ".join(command))
        if error:
            full_error = "\n\n".join(error)
            self.logger.error(f"\n{full_error}")

    def format_std_out(self, std_out):
        """Decode standard output to logger.info"""
        for line in std_out.split(b"\n\n"):
            self.logger.info(line.decode("utf-8"))

    def format_std_err(self, std_err):
        """Decode standard error to logger.error"""
        for line in std_err.split(b"\n\n"):
            self.logger.error(line.decode("utf-8"))

    def debug_std_out(self, std_out):
        """Decode standard output to logger.debug"""
        for line in std_out.split(b"\n\n"):
            self.logger.debug(line.decode("utf-8"))

    def debug_std_err(self, std_err):
        """Decode standard error to logger.debug"""
        for line in std_err.split(b"\n\n"):
            self.logger.debug(line.decode("utf-8"))

    def format_ansible_output(self, process_output: list):
        """Group and format output from ansible execution"""
        std_output = []
        std_warning = []
        std_error = []
        std_complete = []

        for no, line in enumerate(process_output):
            if any(eindicator in line for eindicator in self.error_indicators):
                for pline in process_output[no-2:no]:
                    if any(tindicator in pline for tindicator in self.task_indicators) \
                       or pline == "":
                        std_error.append(pline)
                std_error.append(line)
                for nline in process_output[no+1:self.find_end_of_task(process_output[no+1:],
                                                                       no+1)]:
                    std_error.append(nline)
                std_complete.append(line)
            elif "warn" in line.lower():
                std_warning.append(line)
            else:
                std_output.append(line)
                std_complete.append(line)

        return {
            "output": std_output,
            "warning": std_warning,
            "error": std_error,
            "complete": std_complete
        }

    @staticmethod
    def find_end_of_task(stream_fragment: list, parent_index: int):
        """Parse list of output elements to find beginning of next task and end of current task."""
        for no, line in enumerate(stream_fragment):
            if "changed=true" in line or "changed=false" in line or \
               "An exception occurred during task execution" in line or not line:
                return parent_index + no
        return None
