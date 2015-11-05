package play.templates.types;

import play.Play;
import play.templates.SafeFormatter;
import play.templates.TagContext;
import play.templates.Template;
import play.utils.HTML;

public class SafeHTMLFormatter implements SafeFormatter {

    public String format(Template template, Object value) {
        if (value != null) {
	        if (TagContext.hasParentTag("verbatim") || !Play.configuration.getProperty("future.escapeInTemplates", "false").equals("true")) {
                return value.toString();
            }
            return HTML.htmlEscape(value.toString());
        }
        return "";
    }
}
