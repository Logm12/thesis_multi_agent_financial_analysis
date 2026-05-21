import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Switch } from "@/components/ui/switch";
import { Globe, GraduationCap, User, LogOut, LogIn } from "lucide-react";
import { HeroSection } from "@/components/sections/HeroSection";
import { SecuritySection } from "@/components/sections/SecuritySection";
import { MethodologySection } from "@/components/sections/MethodologySection";
import { VisualizerSection } from "@/components/sections/VisualizerSection";
import { FooterSection } from "@/components/sections/FooterSection";
import { LoginSection } from "@/components/sections/LoginSection";
import { useAuth } from "./lib/auth-context";

type AppView = "landing" | "login";

function App() {
  const { t, i18n } = useTranslation();
  const { isAuthenticated, user, logout } = useAuth();
  const [currentView, setCurrentView] = useState<AppView>("landing");

  const toggleLanguage = () => {
    const currentLang = i18n.language;
    i18n.changeLanguage(currentLang === "vi" ? "en" : "vi");
  };

  const isVietnamese = i18n.language === "vi";

  const handleExperienceClick = () => {
    if (isAuthenticated) {
      // Scroll direct to the visualizer
      document.getElementById("visualizer")?.scrollIntoView({ behavior: "smooth" });
    } else {
      setCurrentView("login");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/40 font-sans antialiased text-slate-900 flex flex-col w-full text-left selection:bg-indigo-100 selection:text-indigo-900">
      
      {/* Optimized Sticky Navbar */}
      <nav className="sticky top-0 z-50 w-full border-b border-slate-200/60 bg-background/80 backdrop-blur-md transition-all">
        <div className="container mx-auto flex h-16 items-center justify-between px-6 md:px-8">
          
          {/* Logo Branding */}
          <button 
            onClick={() => setCurrentView("landing")}
            className="flex items-center gap-2.5 font-bold tracking-tight text-indigo-950 select-none hover:opacity-90 transition-opacity"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-md shadow-indigo-500/20">
              <GraduationCap className="h-5 w-5" />
            </div>
            <span className="text-xl font-extrabold tracking-tight">{t("navbar.brand")}</span>
          </button>

          {/* Action Bar */}
          <div className="flex items-center gap-4 md:gap-6">
            {currentView === "landing" && (
              <div className="hidden md:flex items-center gap-6 text-sm font-semibold text-muted-foreground">
                <a href="#home" className="hover:text-primary transition-colors">{t("navbar.home")}</a>
                <a href="#security" className="hover:text-primary transition-colors">{t("navbar.security")}</a>
                <a href="#methodology" className="hover:text-primary transition-colors">{t("navbar.methodology")}</a>
              </div>
            )}

            {/* i18n Switch Control */}
            <div className="flex items-center gap-3 rounded-full bg-accent/60 hover:bg-accent transition-colors py-1.5 px-3 border border-border">
              <Globe className="h-4 w-4 text-muted-foreground" />
              <span className="text-xs font-bold text-foreground tracking-wider uppercase">
                {isVietnamese ? "VN" : "EN"}
              </span>
              <Switch
                id="language-toggle"
                checked={!isVietnamese}
                onCheckedChange={toggleLanguage}
                className="data-[state=checked]:bg-primary"
              />
            </div>

            {/* Stateful Login Button */}
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-emerald-500/20 bg-emerald-500/5 text-emerald-600 text-xs font-semibold">
                  <User className="w-3.5 h-3.5" />
                  <span>{user?.username}</span>
                </div>
                <button 
                  onClick={logout}
                  className="p-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-destructive transition-colors"
                  title="Log Out"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              currentView !== "login" && (
                <button 
                  onClick={() => setCurrentView("login")}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent/80 hover:bg-accent text-foreground border border-border text-xs font-bold uppercase tracking-wide transition-all shadow-sm active:scale-[0.98]"
                >
                  <LogIn className="w-4 h-4" />
                  <span className="hidden sm:inline">{t("auth.btn_login")}</span>
                </button>
              )
            )}
          </div>
        </div>
      </nav>

      {/* Dynamic Main Content Canvas */}
      <main className="flex-1 w-full">
        {currentView === "login" ? (
          <LoginSection 
            onBack={() => setCurrentView("landing")} 
            onSuccess={() => setCurrentView("landing")} 
          />
        ) : (
          <>
            {/* 1. Hero Anchor */}
            <div id="home">
              <HeroSection onCtaClick={handleExperienceClick} />
            </div>
            
            {/* 2. Security USP */}
            <SecuritySection />
            
            {/* 3. Methodology & Case Studies & Steps */}
            <MethodologySection />
            
            {/* 4. Visualizer & Interactive Demo */}
            <VisualizerSection />
          </>
        )}
      </main>

      {/* Footer */}
      <FooterSection />
    </div>
  );
}

export default App;
