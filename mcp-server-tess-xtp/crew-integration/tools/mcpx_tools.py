from typing import List, Type, Optional, Dict, Any
from pydantic import BaseModel, create_model
from crewai.tools import BaseTool
import requests
import json
import logging

logger = logging.getLogger(__name__)

class MCPTessTool(BaseTool):
    """Adaptador para ferramentas TESS disponíveis via servidor MCP local."""
    name: str
    description: str
    _server_url: str
    _tool_name: str
    
    def _run(self, text: Optional[str] = None, **kwargs) -> str:
        """Executa a ferramenta TESS via servidor MCP local."""
        try:
            # Processar argumentos
            if text and not kwargs:
                try:
                    # Tentar interpretar o texto como JSON
                    input_dict = json.loads(text)
                except json.JSONDecodeError:
                    # Se falhar, usar como texto direto
                    input_dict = {"input_text": text}
            else:
                input_dict = kwargs
            
            logger.info(f"Chamando ferramenta {self._tool_name} com argumentos: {input_dict}")
            
            # Chamar API do servidor MCP
            response = requests.post(
                f"{self._server_url}/tools/call",
                json={"name": self._tool_name, "arguments": input_dict}
            )
            
            result = response.json()
            
            # Verificar erros
            if result.get("isError"):
                error_msg = "Erro na execução"
                if "content" in result and len(result["content"]) > 0:
                    error_msg = result["content"][0].get("text", error_msg)
                raise RuntimeError(error_msg)
            
            # Extrair e formatar resultado
            output = []
            if "content" in result:
                for content_item in result["content"]:
                    if content_item.get("type") == "text" and content_item.get("text"):
                        output.append(content_item["text"])
            
            # Se não houver texto, retornar JSON completo
            if not output:
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta TESS-MCP: {str(e)}")
            return f"❌ Falha na execução: {str(e)}"

def _get_field_type(field_schema: Dict[str, Any]) -> Type:
    """Converte tipo de campo do schema JSON para tipo Python."""
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict
    }
    
    field_type = field_schema.get("type", "string")
    return type_mapping.get(field_type, str)

def _convert_json_schema_to_pydantic(schema: Dict[str, Any], model_name: str = "DynamicModel") -> Type[BaseModel]:
    """Converte schema JSON para modelo Pydantic."""
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    fields = {}
    for field_name, field_schema in properties.items():
        field_type = _get_field_type(field_schema)
        
        # Tratar valores padrão
        default = field_schema.get("default", None)
        if field_name in required:
            # Campos obrigatórios
            fields[field_name] = (field_type, ...)
        else:
            # Campos opcionais com ou sem valor padrão
            fields[field_name] = (Optional[field_type], default)
    
    return create_model(model_name, **fields)

def get_tess_tools(server_url: str = "http://localhost:3001") -> List[BaseTool]:
    """Cria ferramentas CrewAI a partir das ferramentas TESS disponíveis no servidor MCP."""
    tools = []
    
    try:
        # Obter lista de ferramentas do servidor MCP
        response = requests.post(f"{server_url}/tools/list")
        if response.status_code != 200:
            logger.error(f"Erro ao obter lista de ferramentas: {response.status_code}")
            return []
        
        tools_data = response.json().get("tools", [])
        
        # Criar ferramentas CrewAI para cada ferramenta TESS
        for tool_data in tools_data:
            tool_name = tool_data.get("name")
            tool_description = tool_data.get("description", "")
            parameters = tool_data.get("parameters", [])
            
            # Criar schema para a ferramenta
            properties = {}
            required = []
            
            for param in parameters:
                param_name = param.get("name")
                param_schema = {
                    "type": param.get("type", "string"),
                    "description": param.get("description", "")
                }
                
                if "default" in param:
                    param_schema["default"] = param["default"]
                
                properties[param_name] = param_schema
                
                if param.get("required", False):
                    required.append(param_name)
            
            schema = {
                "properties": properties,
                "required": required
            }
            
            # Criar modelo Pydantic para os argumentos
            args_schema = _convert_json_schema_to_pydantic(schema, f"{tool_name}Schema")
            
            # Criar ferramenta CrewAI
            crew_tool = MCPTessTool(
                name=tool_name,
                description=tool_description,
                args_schema=args_schema
            )
            
            # Configurar atributos internos
            crew_tool._server_url = server_url
            crew_tool._tool_name = tool_name
            
            tools.append(crew_tool)
        
        logger.info(f"Carregadas {len(tools)} ferramentas TESS para CrewAI")
        return tools
        
    except Exception as e:
        logger.error(f"Erro ao carregar ferramentas TESS: {str(e)}")
        return [] 