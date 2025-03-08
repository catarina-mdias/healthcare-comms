import os
import tempfile
import unittest
from pathlib import Path

from communication.prompt import PromptTemplate, PromptTemplateModelRole


class TestPromptTemplate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.prompts_dir = Path(self.temp_dir.name)

        self.system_template_file = "system_test.j2"
        with open(
            os.path.join(self.prompts_dir, self.system_template_file), "w"
        ) as f:
            f.write("System template with {{ variable1 }} and {{ variable2 }}")

        self.user_template_file = "user_test.j2"
        with open(
            os.path.join(self.prompts_dir, self.user_template_file), "w"
        ) as f:
            f.write("User template with {{ variable3 }} and {{ variable4 }}")

        self.prompt_template = PromptTemplate(
            system_message_template_file=self.system_template_file,
            user_message_template_file=self.user_template_file,
            prompts_dir=self.prompts_dir,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init(self):
        """Test proper initialization of the PromptTemplate class"""
        # Verify template filenames are stored correctly
        self.assertEqual(
            self.prompt_template._template_filenames[
                PromptTemplateModelRole.SYSTEM_MESSAGE
            ],
            self.system_template_file,
        )
        self.assertEqual(
            self.prompt_template._template_filenames[
                PromptTemplateModelRole.USER_MESSAGE
            ],
            self.user_template_file,
        )

    def test_build_system_message(self):
        """Test building a system message with template variables"""
        result = self.prompt_template.build_system_message(
            variable1="test1", variable2="test2"
        )

        self.assertEqual(result, "System template with test1 and test2")

    def test_build_user_message(self):
        """Test building a user message with template variables"""
        result = self.prompt_template.build_user_message(
            variable3="test3", variable4="test4"
        )

        self.assertEqual(result, "User template with test3 and test4")

    def test_missing_template_variables(self):
        """Test handling of missing template variables"""
        with self.assertRaises(Exception):
            self.prompt_template.build_system_message(variable1="test1")

    def test_extra_template_variables(self):
        """
        Test handling of extra template variables
        Extra variables should be ignored
        """
        result = self.prompt_template.build_system_message(
            variable1="test1", variable2="test2", extra_var="ignored"
        )

        self.assertEqual(result, "System template with test1 and test2")
