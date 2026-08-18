/**
 * Deriva o identificador de registro do Stimulus a partir do caminho do
 * controller que o import.meta.glob de controllers/index.js devolve.
 *
 *   ./hello_controller.js       -> "hello"
 *   ./date_picker_controller.js -> "date-picker"
 */
export function controllerIdentifier(path) {
  return path
    .replace(/^\.\//, "")
    .replace(/_controller\.js$/, "")
    .replaceAll("_", "-");
}
