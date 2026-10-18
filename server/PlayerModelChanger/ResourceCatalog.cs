using System.Security.Cryptography;
using System.Text.Json;

namespace PlayerModelChanger;

// Deployment writes this only after independently validating every VPK member CRC.
public sealed class ResourceCatalog
{
    public Dictionary<string, string> Archives { get; set; } = [];
    public string[] Models { get; set; } = [];
    public string? Failure { get; private set; }
    private readonly HashSet<string> _available = new(StringComparer.Ordinal);
    public bool Allows(string path) => _available.Contains(path);
    public int Count => _available.Count;
    public static ResourceCatalog Load(string file)
    {
        try
        {
            var catalog = JsonSerializer.Deserialize<ResourceCatalog>(File.ReadAllText(file)) ?? throw new InvalidDataException("Empty resource catalog");
            if (catalog.Archives.Count == 0) throw new InvalidDataException("No verified VPK archives");
            foreach (var (path, hash) in catalog.Archives)
            {
                using var stream = File.OpenRead(path);
                if (!Convert.ToHexString(SHA256.HashData(stream)).Equals(hash, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException("VPK changed: " + Path.GetFileName(path));
            }
            foreach (var model in catalog.Models)
            {
                if (!(model.StartsWith("characters/", StringComparison.Ordinal) || model.StartsWith("phase2/characters/", StringComparison.Ordinal)) || !model.EndsWith(".vmdl", StringComparison.Ordinal) ||
                    model.Contains("..", StringComparison.Ordinal) || model.Contains('\\'))
                    throw new InvalidDataException("Invalid model resource path");
                catalog._available.Add(model);
            }
            return catalog;
        }
        catch (Exception e) when (e is IOException or InvalidDataException or UnauthorizedAccessException or JsonException or ArgumentException)
        { return new ResourceCatalog { Failure = e.Message }; }
    }
}
