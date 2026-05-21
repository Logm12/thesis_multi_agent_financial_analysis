import { useTranslation } from "react-i18next";
import { GraduationCap } from "lucide-react";

export function FooterSection() {
  const { t } = useTranslation();
  
  return (
    <footer className="py-12 bg-background border-t border-border px-6 flex justify-center flex-col items-center text-center">
      <div className="max-w-5xl w-full flex flex-col items-center space-y-6">
        <div className="flex items-center gap-2 font-bold text-primary select-none">
          <GraduationCap className="w-6 h-6" />
          <span>Lumo Thesis Platform</span>
        </div>
        
        <div className="w-16 h-px bg-border" />
        
        <p className="text-sm text-muted-foreground leading-relaxed">
          {t("footer.copyright")}
        </p>
        
        <p className="text-xs text-muted-foreground/60">
          Built with React, Tailwind CSS, and Vite. All computations local.
        </p>
      </div>
    </footer>
  );
}
