import { Application } from "@hotwired/stimulus";

import { controllerIdentifier } from "../lib/stimulus-identifier.js";

const application = Application.start();

// Registra automaticamente todo *_controller.js deste diretorio.
// O nome do controller vem do arquivo: hello_controller.js -> data-controller="hello".
const modules = import.meta.glob("./*_controller.js", { eager: true });

for (const [path, module] of Object.entries(modules)) {
  application.register(controllerIdentifier(path), module.default);
}

export { application };
