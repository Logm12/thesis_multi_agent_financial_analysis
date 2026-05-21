import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export function HeroSection({ onCtaClick }: { onCtaClick?: () => void }) {
  const { t } = useTranslation();

  return (
    <section className="relative pt-20 pb-16 md:pt-32 md:pb-24 overflow-hidden bg-background flex items-center justify-center flex-col text-center px-6">
      {/* Background subtle glow */}
      <div className="absolute inset-0 -z-10 flex items-center justify-center opacity-20">
        <div className="w-[400px] h-[400px] bg-primary rounded-full blur-[120px]" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/30 bg-primary/10 text-primary text-sm font-medium mb-6 backdrop-blur-md hover:border-primary/50 transition-colors"
      >
        <Sparkles className="w-4 h-4" />
        <span>{t("hero.badge")}</span>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="text-4xl md:text-6xl font-extrabold tracking-tight max-w-3xl bg-clip-text text-transparent bg-gradient-to-b from-foreground to-foreground/70 mb-6 leading-[1.15]"
      >
        {t("hero.title")}
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-8 leading-relaxed"
      >
        {t("hero.subtitle")}
      </motion.p>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex gap-4 flex-col sm:flex-row items-center justify-center"
      >
        <Button
          size="lg"
          onClick={onCtaClick}
          className="px-8 py-6 h-auto text-lg font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_35px_rgba(79,70,229,0.6)] hover:scale-[1.03] active:scale-[0.98] group flex gap-2 items-center"
        >
          {t("hero.cta")}
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </Button>
      </motion.div>
    </section>
  );
}
