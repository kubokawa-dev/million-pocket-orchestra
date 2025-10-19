import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";
import "./common/types.tsp";
import "./common/errors.tsp";
import "./models/user.tsp";
import "./models/draw.tsp";
import "./models/prediction.tsp";
import "./models/social.tsp";
import "./routes/auth.tsp";
import "./routes/draws.tsp";
import "./routes/predictions.tsp";
import "./routes/users.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

@service({
  title: "Million Pocket API",
})
@server("http://localhost:8787", "Local development server")
@server("https://api.million-pocket.app", "Production server")
namespace MillionPocketAPI;
