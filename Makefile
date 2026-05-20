ADDON_PACKAGE := preview_due_button
DIST_DIR := dist
ARTIFACT := $(DIST_DIR)/$(ADDON_PACKAGE).ankiaddon

.PHONY: syntax package clean

syntax:
	python3 -c "import ast, pathlib; ast.parse(pathlib.Path('$(ADDON_PACKAGE)/__init__.py').read_text())"

package: syntax
	mkdir -p $(DIST_DIR)
	rm -f $(ARTIFACT)
	cd $(ADDON_PACKAGE) && zip -r ../$(ARTIFACT) . -x "__pycache__/*" "*.pyc" ".DS_Store"

clean:
	rm -rf $(DIST_DIR) $(ADDON_PACKAGE)/__pycache__
