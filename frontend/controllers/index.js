import { Application } from "@hotwired/stimulus";

const application = Application.start();

// Registra automaticamente todo *_controller.js deste diretorio.
// O nome do controller vem do arquivo: hello_controller.js -> data-controller="hello".
const modules = import.meta.glob("./*_controller.js", { eager: true });

for (const [path, module] of Object.entries(modules)) {
  const identifier = path
    .replace(/^\.\//, "")
    .replace(/_controller\.js$/, "")
    .replaceAll("_", "-");

  application.register(identifier, module.default);
}

export { application };
